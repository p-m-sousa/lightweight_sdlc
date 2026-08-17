#!/usr/bin/env python3
"""Audit the authority that actually ran against the authority each role declared.

Pinning authority in an agent definition is the preventive control: it removes
the spawn-time attribute a caller could forget. This is the detective control
behind it, and it instruments nothing new. The runtime already writes one
rollout log per session recording the role that ran, the model, the reasoning
effort, and token usage; this reads those logs and reports what they show.

Modes:
  compliance  check every review session against its role's declared authority,
              and every attributable unit against its declared review route,
              failing on any violation not recorded in the shrink-only baseline.
  usage       roll up input, cached-input, and output tokens by role and by unit.

Attribution is exact or absent. A delegate names its assigned record when it
generates the phase packet, so that command identifies the unit; a session
without it is reported as unattributed rather than guessed at from free-text
mentions, which would attribute a session to every record it happened to read.

A fresh harness copy has no session history. Absence of evidence is reported as
`no history` and exits 0; only recorded evidence of a violation fails.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    tomllib = None


AUTHORITY_RELATIVE = ".codex/authority.toml"
BASELINE_RELATIVE = ".codex/authority_baseline.json"
FEATURE_GLOB = "docs/features/FEAT-*.md"
REVIEW_ROUTE = re.compile(r"^-\s+Review route:\s*(.+?)\s*$", re.MULTILINE)
PLACEHOLDER = re.compile(r"^\[[A-Z0-9_]+\]$")

EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_CONFIGURATION = 2


@dataclass
class Session:
    path: Path
    role: str = ""
    cwd: str = ""
    model: str = ""
    effort: str = ""
    unit: str = ""
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True)
class Violation:
    kind: str
    subject: str
    role: str
    observed: str
    expected: str
    session: str

    def key(self) -> tuple[str, str, str, str]:
        return (self.kind, self.subject, self.role, self.observed)


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / AUTHORITY_RELATIVE).is_file():
            return candidate
    raise SystemExit("Could not find a harness project root from the current directory.")


def load_authority(root: Path) -> dict:
    if tomllib is None:
        raise SystemExit("Python 3.11+ is required to read the authority table.")
    path = root / AUTHORITY_RELATIVE
    if not path.is_file():
        raise SystemExit(f"Missing authority table: {AUTHORITY_RELATIVE}")
    with path.open("rb") as handle:
        return tomllib.load(handle)


def expected_authority(authority: dict, agent: str) -> str:
    role = authority.get("roles", {}).get(agent)
    if not role:
        raise SystemExit(f"Authority table declares no role named {agent!r}.")
    model = authority.get("models", {}).get(role["model"])
    if model is None:
        raise SystemExit(f"Authority table declares no model key {role['model']!r}.")
    return f"{model}/{role['effort']}"


def unresolved_placeholders(authority: dict) -> list[str]:
    return sorted(value for value in authority.get("models", {}).values() if PLACEHOLDER.match(value))


def sessions_directory(authority: dict, override: str | None) -> Path:
    configured = override or authority.get("sessions", {}).get("directory", "~/.codex/sessions")
    return Path(configured).expanduser()


def read_session(path: Path, unit_pattern: re.Pattern[str]) -> Session:
    """Harvest one rollout log. Later turn contexts and token counts supersede earlier ones."""
    session = Session(path=path)
    try:
        handle = path.open(encoding="utf-8", errors="replace")
    except OSError:
        return session
    with handle:
        for line in handle:
            if not session.unit:
                found = unit_pattern.search(line)
                if found:
                    session.unit = found.group(1)
            if '"session_meta"' not in line and '"turn_context"' not in line and '"token_count"' not in line:
                continue
            try:
                event = json.loads(line)
            except ValueError:
                continue
            payload = event.get("payload")
            if not isinstance(payload, dict):
                continue
            kind = event.get("type")
            if kind == "session_meta":
                session.role = payload.get("agent_role") or ""
                session.cwd = payload.get("cwd") or ""
            elif kind == "turn_context":
                session.model = payload.get("model") or session.model
                session.effort = payload.get("effort") or session.effort
            elif payload.get("type") == "token_count":
                usage = (payload.get("info") or {}).get("total_token_usage") or {}
                session.input_tokens = usage.get("input_tokens", session.input_tokens)
                session.cached_input_tokens = usage.get("cached_input_tokens", session.cached_input_tokens)
                session.output_tokens = usage.get("output_tokens", session.output_tokens)
    return session


def collect_sessions(root: Path, directory: Path, authority: dict) -> list[Session]:
    settings = authority.get("sessions", {})
    pattern = re.compile(settings.get("unit_pattern", r"--feature\s+\S*?(FEAT-[0-9]{3})\.md"))
    if not directory.is_dir():
        return []
    inside = str(root.resolve())
    collected = []
    for path in sorted(directory.glob(settings.get("glob", "**/rollout-*.jsonl"))):
        session = read_session(path, pattern)
        if session.cwd == inside or session.cwd.startswith(inside + "/"):
            collected.append(session)
    return collected


def declared_routes(root: Path) -> dict[str, str]:
    routes = {}
    for path in sorted(root.glob(FEATURE_GLOB)):
        match = REVIEW_ROUTE.search(path.read_text(encoding="utf-8", errors="replace"))
        if match:
            routes[path.stem] = match.group(1).strip().strip("`")
    return routes


def load_baseline(path: Path) -> set[tuple[str, str, str, str]]:
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        (entry["kind"], entry["subject"], entry["role"], entry["observed"])
        for entry in data.get("accepted_violations", [])
    }


def review_violations(authority: dict, sessions: list[Session], declared: dict[str, str]) -> list[Violation]:
    routes = authority.get("routes", {}).get("review", {})
    audited = set(authority.get("audit", {}).get("review_roles", list(routes.values())))
    violations: list[Violation] = []
    for session in sorted(sessions, key=lambda item: item.path.name):
        if session.role not in audited:
            continue
        # Exact and attribution-free: a role that ran below its own declared
        # authority is the silent fallback this control exists to catch.
        observed = f"{session.model or '?'}/{session.effort or '?'}"
        expected = expected_authority(authority, session.role)
        if observed != expected:
            violations.append(Violation("authority", session.role, session.role, observed, expected, session.path.name))
        # Exact where the session named its assigned record.
        route = declared.get(session.unit)
        if route and routes.get(route) and session.role != routes[route]:
            violations.append(
                Violation("route", session.unit, session.role, session.role, routes[route], session.path.name)
            )
    return violations


def compliance(root: Path, authority: dict, sessions: list[Session], baseline: Path) -> int:
    routes = authority.get("routes", {}).get("review", {})
    audited = set(authority.get("audit", {}).get("review_roles", list(routes.values())))
    declared = declared_routes(root)
    reviews = [session for session in sessions if session.role in audited]

    print(f"Compliance: {len(declared)} unit(s) declare a review route; {len(reviews)} review session(s) in history.")
    if not reviews:
        print("  No history: no review sessions recorded for this project. Nothing to check.")
        return EXIT_OK

    unknown = sorted({session.unit for session in reviews if session.unit and session.unit not in declared})
    unattributed = sum(1 for session in reviews if not session.unit)
    covered = {session.unit for session in reviews if session.unit in declared}
    print(f"  Attributed to a declared unit: {len(reviews) - unattributed - len(unknown)}; unattributed: {unattributed}.")
    missing = sorted(set(declared) - covered)
    if missing:
        print(f"  No attributable review session for: {', '.join(missing)} (reported, not a violation).")

    accepted = load_baseline(baseline)
    violations = review_violations(authority, reviews, declared)
    outstanding = [violation for violation in violations if violation.key() not in accepted]
    if len(violations) - len(outstanding):
        print(f"  {len(violations) - len(outstanding)} violation(s) accepted by {baseline.name}.")
    if not outstanding:
        print("  Every review session ran at its declared authority.")
        return EXIT_OK

    print(f"  {len(outstanding)} violation(s) outside the baseline:")
    for violation in outstanding:
        if violation.kind == "authority":
            detail = f"{violation.role} ran {violation.observed}, declared {violation.expected}"
        else:
            detail = f"{violation.subject} declared {violation.expected} but was reviewed by {violation.observed}"
        print(f"  - [{violation.kind}] {detail} ({violation.session})")
    return EXIT_VIOLATION


def usage(sessions: list[Session]) -> int:
    by_role: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    by_unit: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for session in sessions:
        counts = (session.input_tokens, session.cached_input_tokens, session.output_tokens)
        for table, key in ((by_role, session.role or "(primary)"), (by_unit, session.unit or "(unattributed)")):
            row = table[key]
            row[0] += 1
            for offset, value in enumerate(counts, start=1):
                row[offset] += value

    for title, table in (("By role", by_role), ("By unit", by_unit)):
        print(f"\n{title}")
        print(f"  {'key':<24}{'sessions':>9}{'input':>14}{'cached':>14}{'output':>10}")
        for key, row in sorted(table.items(), key=lambda entry: -entry[1][3]):
            print(f"  {key:<24}{row[0]:>9}{row[1]:>14}{row[2]:>14}{row[3]:>10}")
    return EXIT_OK


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=("compliance", "usage"), default="compliance")
    parser.add_argument("--root", type=Path, help="Project root; defaults to discovery from the current directory.")
    parser.add_argument("--sessions-dir", help="Override the session-log directory declared in the authority table.")
    parser.add_argument("--baseline", type=Path, help=f"Accepted-gap baseline; defaults to {BASELINE_RELATIVE}.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve() if args.root else find_root(Path.cwd().resolve())
    authority = load_authority(root)
    directory = sessions_directory(authority, args.sessions_dir)

    sessions = collect_sessions(root, directory, authority)
    if not sessions:
        print(f"No history: no session logs for this project under {directory}. Nothing to audit.")
        return EXIT_OK

    print(f"Harvested {len(sessions)} session log(s) for {root} from {directory}.")
    if args.mode == "usage":
        return usage(sessions)

    pending = unresolved_placeholders(authority)
    if pending:
        print(
            f"Cannot audit compliance: {AUTHORITY_RELATIVE} still holds placeholder model(s) {', '.join(pending)}."
            " Fill in the authority table before auditing recorded history.",
            file=sys.stderr,
        )
        return EXIT_CONFIGURATION
    return compliance(root, authority, sessions, args.baseline or (root / BASELINE_RELATIVE))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:  # pragma: no cover - piped output
        sys.exit(EXIT_OK)
