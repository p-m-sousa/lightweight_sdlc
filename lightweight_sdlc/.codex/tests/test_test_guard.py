from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
GUARD_PATH = ROOT / ".codex/scripts/test_guard.py"
SPEC = importlib.util.spec_from_file_location("test_guard", GUARD_PATH)
assert SPEC and SPEC.loader
guard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = guard
SPEC.loader.exec_module(guard)


class TestGuardTests(unittest.TestCase):
    def resources(self, **changes: object) -> guard.Resources:
        values = {
            "host_cpus": 12,
            "effective_cpus": 8,
            "host_memory_bytes": 32 * guard.GIB,
            "effective_memory_bytes": 16 * guard.GIB,
            "available_memory_bytes": 10 * guard.GIB,
            "disk_total_bytes": 100 * guard.GIB,
            "disk_free_bytes": 40 * guard.GIB,
            "constrained_by": ("cgroup-memory",),
            "inspection_warnings": (),
        }
        values.update(changes)
        return guard.Resources(**values)

    def test_policy_is_bounded_and_deterministic(self) -> None:
        resources = self.resources()
        policy = guard.derive_policy(resources)
        reserve = resources.effective_memory_bytes * 15 // 100
        self.assertEqual(policy.max_rss_bytes, resources.available_memory_bytes - reserve)
        self.assertEqual(policy.max_workers, 6)
        self.assertEqual(policy.timeout_seconds, 1800)
        self.assertEqual(policy.minimum_free_disk_bytes, 2 * guard.GIB)

        large = guard.derive_policy(
            self.resources(
                effective_memory_bytes=64 * guard.GIB,
                available_memory_bytes=50 * guard.GIB,
                effective_cpus=32,
            )
        )
        self.assertEqual(large.max_rss_bytes, 50 * guard.GIB - (64 * guard.GIB * 15 // 100))
        self.assertEqual(large.max_workers, 31)

    def test_current_pressure_reduces_budget_and_workers(self) -> None:
        policy = guard.derive_policy(self.resources(available_memory_bytes=3 * guard.GIB))
        self.assertEqual(policy.max_rss_bytes, 3 * guard.GIB - (16 * guard.GIB * 15 // 100))
        self.assertEqual(policy.max_workers, 1)

    def test_limit_increase_requires_explicit_approved_override(self) -> None:
        policy = guard.derive_policy(self.resources())
        with self.assertRaisesRegex(ValueError, "approved-override"):
            guard.apply_overrides(policy, 13000, None, None, False)
        raised = guard.apply_overrides(policy, 13000, 9, 1900, True)
        self.assertEqual(raised.max_rss_bytes, 13000 * guard.MIB)
        self.assertEqual(raised.max_workers, 9)
        self.assertEqual(raised.timeout_seconds, 1900)

    def test_lower_limits_need_no_override(self) -> None:
        policy = guard.derive_policy(self.resources())
        lowered = guard.apply_overrides(policy, 1024, 2, 60, False)
        self.assertEqual(lowered.max_rss_bytes, guard.GIB)
        self.assertEqual(lowered.max_workers, 2)
        self.assertEqual(lowered.timeout_seconds, 60)

    def test_child_environment_clamps_user_parallelism_and_node_heap(self) -> None:
        policy = guard.derive_policy(self.resources())
        child = guard.child_environment(
            {
                "GOMAXPROCS": "99",
                "JOBS": "2",
                "NODE_OPTIONS": "--trace-warnings --max_old_space_size=99999",
            },
            policy,
        )
        self.assertEqual(child["GOMAXPROCS"], "6")
        self.assertEqual(child["JOBS"], "2")
        self.assertIn("--trace-warnings", child["NODE_OPTIONS"])
        expected_heap = int((policy.max_rss_bytes // guard.MIB) * 0.70)
        self.assertIn(f"--max-old-space-size={expected_heap}", child["NODE_OPTIONS"])
        self.assertNotIn("99999", child["NODE_OPTIONS"])

    def test_low_headroom_fails_closed(self) -> None:
        resources = self.resources(available_memory_bytes=2200 * guard.MIB)
        policy = guard.derive_policy(resources)
        self.assertLess(policy.max_rss_bytes, 512 * guard.MIB)
        with self.assertRaisesRegex(RuntimeError, "safe test memory"):
            guard.ensure_runnable(resources, policy)

    def test_missing_process_inspection_warns_and_runs(self) -> None:
        resources = self.resources()
        policy = guard.derive_policy(resources)

        class FinishedProcess:
            pid = 123
            returncode = 0

            def poll(self) -> int:
                return 0

        errors = io.StringIO()
        with (
            patch.object(guard, "detect_resources", return_value=resources),
            patch.object(guard, "process_tree_rss", return_value=None),
            patch.object(guard.subprocess, "Popen", return_value=FinishedProcess()),
            contextlib.redirect_stderr(errors),
        ):
            result = guard.run_guarded(["example-test"], ROOT, policy)

        self.assertEqual(result, 0)
        self.assertIn("inspection is unavailable", errors.getvalue())

    def test_graceful_stop_escalates_and_reaps(self) -> None:
        class StubbornProcess:
            pid = 123

            def __init__(self) -> None:
                self.waits = 0

            def wait(self, timeout: int) -> int:
                self.waits += 1
                if self.waits == 1:
                    raise guard.subprocess.TimeoutExpired("test", timeout)
                return 0

            def kill(self) -> None:
                pass

            def terminate(self) -> None:
                pass

        process = StubbornProcess()
        with patch.object(guard.os, "killpg") as killpg:
            guard.terminate_group(process, force=False)

        self.assertEqual(process.waits, 2)
        self.assertEqual(
            [call.args[1] for call in killpg.call_args_list],
            [guard.signal.SIGTERM, guard.signal.SIGKILL],
        )


if __name__ == "__main__":
    unittest.main()
