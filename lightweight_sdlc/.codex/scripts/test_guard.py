#!/usr/bin/env python3
"""Detect local capacity and run tests with deterministic resource guardrails."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Mapping, Optional, Sequence, Tuple


MIB = 1024**2
GIB = 1024**3
DEFAULT_TIMEOUT_SECONDS = 30 * 60
POLL_SECONDS = 0.25
RESOURCE_EXIT = 125
TIMEOUT_EXIT = 124
MEMORY_EXIT = 137
DISK_EXIT = 138
NUMERIC_WORKER_ENV = (
    "CARGO_BUILD_JOBS",
    "GOMAXPROCS",
    "JOBS",
    "NX_PARALLEL",
    "PYTEST_XDIST_AUTO_NUM_WORKERS",
    "RAYON_NUM_THREADS",
    "TURBO_CONCURRENCY",
    "UV_CONCURRENT_BUILDS",
    "UV_CONCURRENT_DOWNLOADS",
    "UV_CONCURRENT_INSTALLS",
    "VITEST_MAX_THREADS",
)


@dataclass(frozen=True)
class Resources:
    host_cpus: int
    effective_cpus: int
    host_memory_bytes: int
    effective_memory_bytes: int
    available_memory_bytes: int
    disk_total_bytes: int
    disk_free_bytes: int
    constrained_by: Tuple[str, ...]
    inspection_warnings: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Policy:
    max_workers: int
    max_rss_bytes: int
    emergency_free_memory_bytes: int
    minimum_free_disk_bytes: int
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS


def read_int(path: Path) -> Optional[int]:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return None
    if value == "max":
        return None
    try:
        parsed = int(value)
    except ValueError:
        return None
    return None if parsed >= 1 << 60 else parsed


def linux_memory() -> Tuple[Optional[int], Optional[int]]:
    try:
        rows = (Path("/proc/meminfo").read_text(encoding="utf-8"))
    except OSError:
        return None, None
    values = {key: int(value.split()[0]) * 1024 for key, value in re.findall(r"^(\w+):\s+(.+)$", rows, re.MULTILINE)}
    return values.get("MemTotal"), values.get("MemAvailable")


def mac_memory() -> Tuple[Optional[int], Optional[int]]:
    try:
        total_result = subprocess.run(
            ["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, check=False
        )
        vm_result = subprocess.run(["vm_stat"], capture_output=True, text=True, check=False)
    except OSError:
        return None, None
    if total_result.returncode or vm_result.returncode:
        return None, None
    try:
        total = int(total_result.stdout.strip())
        page_match = re.search(r"page size of (\d+) bytes", vm_result.stdout)
        page_size = int(page_match.group(1)) if page_match else 4096
        pages = {
            key: int(value.replace(".", ""))
            for key, value in re.findall(r"^Pages (free|inactive|speculative|purgeable):\s+(\d+\.)$", vm_result.stdout, re.MULTILINE)
        }
        available = sum(pages.values()) * page_size
    except (AttributeError, ValueError):
        return None, None
    return total, available


def cgroup_memory() -> Tuple[Optional[int], Optional[int]]:
    pairs = (
        (Path("/sys/fs/cgroup/memory.max"), Path("/sys/fs/cgroup/memory.current")),
        (
            Path("/sys/fs/cgroup/memory/memory.limit_in_bytes"),
            Path("/sys/fs/cgroup/memory/memory.usage_in_bytes"),
        ),
    )
    for limit_path, used_path in pairs:
        limit = read_int(limit_path)
        if limit is not None:
            return limit, read_int(used_path)
    return None, None


def cgroup_cpus() -> Optional[int]:
    try:
        value = Path("/sys/fs/cgroup/cpu.max").read_text(encoding="utf-8").strip().split()
        if len(value) == 2 and value[0] != "max":
            return max(1, int(int(value[0]) / int(value[1])))
    except (OSError, ValueError, ZeroDivisionError):
        pass
    quota = read_int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us"))
    period = read_int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us"))
    if quota is not None and quota > 0 and period:
        return max(1, int(quota / period))
    return None


def detect_resources(root: Path) -> Resources:
    host_cpus = max(1, os.cpu_count() or 1)
    warnings = []
    total, available = linux_memory()
    if total is None:
        total, available = mac_memory()
    if total is None:
        try:
            total = int(os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE"))
        except (AttributeError, OSError, ValueError):
            total, available = 2 * GIB, 1 * GIB
            warnings.append("memory capacity unavailable; using a conservative 2 GiB/1 GiB fallback")
    constrained = []
    cpu_limit = cgroup_cpus()
    effective_cpus = min(host_cpus, cpu_limit) if cpu_limit else host_cpus
    if cpu_limit and cpu_limit < host_cpus:
        constrained.append("cgroup-cpu")
    memory_limit, memory_used = cgroup_memory()
    effective_total = min(total, memory_limit) if memory_limit else total
    if memory_limit and memory_limit < total:
        constrained.append("cgroup-memory")
    if available is None:
        available = effective_total * 3 // 4
        constrained.append("bounded-availability-fallback")
        warnings.append("available memory unavailable; using 75% of effective capacity")
    if memory_limit and memory_used is not None:
        available = min(available, max(0, memory_limit - memory_used))
    disk = shutil.disk_usage(root)
    return Resources(
        host_cpus=host_cpus,
        effective_cpus=effective_cpus,
        host_memory_bytes=total,
        effective_memory_bytes=effective_total,
        available_memory_bytes=min(available, effective_total),
        disk_total_bytes=disk.total,
        disk_free_bytes=disk.free,
        constrained_by=tuple(constrained),
        inspection_warnings=tuple(warnings),
    )


def derive_policy(resources: Resources) -> Policy:
    memory_reserve = resources.effective_memory_bytes * 15 // 100
    safe_rss = min(
        resources.effective_memory_bytes * 65 // 100,
        max(0, resources.available_memory_bytes - memory_reserve),
    )
    memory_workers = max(1, safe_rss // (1280 * MIB))
    cpu_workers = max(1, resources.effective_cpus - 1)
    workers = max(1, min(cpu_workers, memory_workers))
    return Policy(
        max_workers=workers,
        max_rss_bytes=safe_rss,
        emergency_free_memory_bytes=resources.effective_memory_bytes * 5 // 100,
        minimum_free_disk_bytes=max(
            512 * MIB,
            min(resources.disk_total_bytes * 2 // 100, resources.disk_free_bytes * 20 // 100),
        ),
    )


def apply_overrides(
    policy: Policy,
    memory_mib: Optional[int],
    workers: Optional[int],
    timeout_seconds: Optional[int],
    allow_increase: bool,
) -> Policy:
    requested = replace(
        policy,
        max_rss_bytes=(memory_mib * MIB if memory_mib is not None else policy.max_rss_bytes),
        max_workers=(workers if workers is not None else policy.max_workers),
        timeout_seconds=(timeout_seconds if timeout_seconds is not None else policy.timeout_seconds),
    )
    increased = (
        requested.max_rss_bytes > policy.max_rss_bytes
        or requested.max_workers > policy.max_workers
        or requested.timeout_seconds > policy.timeout_seconds
    )
    if increased and not allow_increase:
        raise ValueError("raising an automatic safety limit requires --approved-override")
    return requested


def child_environment(base: Mapping[str, str], policy: Policy) -> dict[str, str]:
    child = dict(base)
    for name in NUMERIC_WORKER_ENV:
        try:
            current = int(child.get(name, policy.max_workers))
        except ValueError:
            current = policy.max_workers
        child[name] = str(min(current, policy.max_workers))
    heap_mib = max(256, int((policy.max_rss_bytes // MIB) * 0.70))
    node_options = child.get("NODE_OPTIONS", "")
    heap_pattern = re.compile(r"--max[-_]old[-_]space[-_]size(?:=|\s+)\d+")
    match = heap_pattern.search(node_options)
    if match:
        existing = int(re.search(r"\d+", match.group()).group())
        node_options = heap_pattern.sub(f"--max-old-space-size={min(existing, heap_mib)}", node_options)
    else:
        node_options = f"{node_options} --max-old-space-size={heap_mib}".strip()
    child["NODE_OPTIONS"] = node_options
    child["TEST_RESOURCE_MAX_RSS_MIB"] = str(policy.max_rss_bytes // MIB)
    child["TEST_RESOURCE_WORKERS"] = str(policy.max_workers)
    return child


def process_tree_rss(root_pid: int) -> Optional[int]:
    try:
        result = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,rss="], capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    if result.returncode:
        return None
    rows = []
    for line in result.stdout.splitlines():
        try:
            pid, parent, rss_kib = (int(value) for value in line.split())
        except ValueError:
            continue
        rows.append((pid, parent, rss_kib))
    descendants = {root_pid}
    while True:
        added = {pid for pid, parent, _ in rows if parent in descendants} - descendants
        if not added:
            break
        descendants.update(added)
    return sum(rss_kib * 1024 for pid, _, rss_kib in rows if pid in descendants)


def terminate_group(process: subprocess.Popen[bytes], force: bool) -> None:
    def send(kill: bool) -> None:
        try:
            os.killpg(process.pid, signal.SIGKILL if kill else signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            try:
                process.kill() if kill else process.terminate()
            except OSError:
                pass

    send(force)
    try:
        process.wait(timeout=2)
        return
    except subprocess.TimeoutExpired:
        if not force:
            send(True)
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass


def ensure_runnable(resources: Resources, policy: Policy) -> None:
    if policy.max_rss_bytes < 512 * MIB:
        raise RuntimeError("less than 512 MiB of safe test memory is available")
    if resources.disk_free_bytes <= policy.minimum_free_disk_bytes:
        raise RuntimeError("free disk is below the deterministic reserve")


def run_guarded(command: Sequence[str], root: Path, policy: Policy) -> int:
    resources = detect_resources(root)
    ensure_runnable(resources, policy)
    for warning in resources.inspection_warnings:
        print(f"test guard warning: {warning}", file=sys.stderr)
    monitor_rss = process_tree_rss(os.getpid()) is not None
    if not monitor_rss:
        print(
            "test guard warning: process-tree RSS inspection is unavailable; continuing with bounded worker and heap caps",
            file=sys.stderr,
        )
    process = subprocess.Popen(
        list(command),
        cwd=str(root),
        env=child_environment(os.environ, policy),
        start_new_session=True,
    )
    started = time.monotonic()
    sample = 0
    while process.poll() is None:
        rss = process_tree_rss(process.pid) if monitor_rss else None
        if monitor_rss and rss is None:
            monitor_rss = False
            print(
                "test guard warning: process-tree RSS inspection was lost; continuing with bounded worker and heap caps",
                file=sys.stderr,
            )
        if rss is not None and rss > policy.max_rss_bytes:
            terminate_group(process, force=True)
            print(
                f"test guard stopped: process tree used {rss // MIB} MiB; limit is {policy.max_rss_bytes // MIB} MiB",
                file=sys.stderr,
            )
            return MEMORY_EXIT
        if time.monotonic() - started > policy.timeout_seconds:
            terminate_group(process, force=False)
            print(f"test guard stopped: exceeded {policy.timeout_seconds}s", file=sys.stderr)
            return TIMEOUT_EXIT
        if sample % 4 == 0:
            current = detect_resources(root)
            if current.available_memory_bytes < policy.emergency_free_memory_bytes:
                terminate_group(process, force=True)
                print("test guard stopped: system memory reached the emergency reserve", file=sys.stderr)
                return MEMORY_EXIT
            if current.disk_free_bytes < policy.minimum_free_disk_bytes:
                terminate_group(process, force=True)
                print("test guard stopped: disk reached the minimum free reserve", file=sys.stderr)
                return DISK_EXIT
        sample += 1
        time.sleep(POLL_SECONDS)
    return int(process.returncode or 0)


def summary(resources: Resources, policy: Policy) -> dict[str, object]:
    return {
        "resources": {
            **asdict(resources),
            "constrained_by": list(resources.constrained_by),
        },
        "policy": asdict(policy),
        "process_tree_rss_inspection": process_tree_rss(os.getpid()) is not None,
        "runnable": policy.max_rss_bytes >= 512 * MIB
        and resources.disk_free_bytes > policy.minimum_free_disk_bytes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Test working directory.")
    parser.add_argument("--json", action="store_true", help="Emit the detected policy as JSON.")
    parser.add_argument("--memory-mib", type=int, help="Lower memory limit, or an approved override.")
    parser.add_argument("--workers", type=int, help="Lower worker cap, or an approved override.")
    parser.add_argument("--timeout-seconds", type=int, help="Lower timeout, or an approved override.")
    parser.add_argument(
        "--approved-override",
        action="store_true",
        help="Assert that the user approved increasing an automatic safety limit.",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Test command after --; omit to inspect.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if args.memory_mib is not None and args.memory_mib < 1:
        raise ValueError("--memory-mib must be positive")
    if args.workers is not None and args.workers < 1:
        raise ValueError("--workers must be positive")
    if args.timeout_seconds is not None and args.timeout_seconds < 1:
        raise ValueError("--timeout-seconds must be positive")
    resources = detect_resources(root)
    policy = apply_overrides(
        derive_policy(resources),
        args.memory_mib,
        args.workers,
        args.timeout_seconds,
        args.approved_override,
    )
    command = list(args.command)
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        print(json.dumps(summary(resources, policy), sort_keys=True, indent=2 if args.json else None))
        return 0
    print(json.dumps(summary(resources, policy), sort_keys=True), file=sys.stderr)
    return run_guarded(command, root, policy)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"test guard blocked: {exc}", file=sys.stderr)
        sys.exit(RESOURCE_EXIT)
