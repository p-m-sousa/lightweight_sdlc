from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / ".codex/scripts/authority_audit.py"
SPEC = importlib.util.spec_from_file_location("authority_audit", AUDIT_PATH)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)

SUBAGENT = "test-subagent-model"
ELEVATED = "test-elevated-model"


def rollout(cwd: Path, role: str, model: str, effort: str, unit: str | None, tokens: tuple[int, int, int]) -> str:
    """One synthetic rollout log in the shape the runtime already writes."""
    lines = [
        {"type": "session_meta", "payload": {"agent_role": role, "cwd": str(cwd)}},
        {"type": "turn_context", "payload": {"model": model, "effort": effort}},
    ]
    if unit:
        command = f"python3 -B .codex/scripts/context_router.py review --feature docs/features/{unit}.md"
        lines.append({"type": "response_item", "payload": {"type": "custom_tool_call", "input": command}})
    lines.append(
        {
            "type": "event_msg",
            "payload": {
                "type": "token_count",
                "info": {
                    "total_token_usage": {
                        "input_tokens": tokens[0],
                        "cached_input_tokens": tokens[1],
                        "output_tokens": tokens[2],
                    }
                },
            },
        }
    )
    return "\n".join(json.dumps(line) for line in lines) + "\n"


class AuthorityAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / ".codex").mkdir(parents=True)
        (self.root / "docs/features").mkdir(parents=True)
        self.sessions = self.root / "sessions"
        self.sessions.mkdir()
        self.instantiate_authority()

    def instantiate_authority(self, *, placeholders: bool = False) -> None:
        table = (ROOT / ".codex/authority.toml").read_text()
        if not placeholders:
            table = table.replace("[SUBAGENT_MODEL]", SUBAGENT).replace("[ELEVATED_MODEL]", ELEVATED)
            table = table.replace("[PRIMARY_MODEL]", ELEVATED)
        (self.root / ".codex/authority.toml").write_text(table)
        self.authority = audit.load_authority(self.root)

    def declare(self, unit: str, route: str) -> None:
        (self.root / f"docs/features/{unit}.md").write_text(
            f"# {unit} Example\n\n- Status: Testing\n- Review route: {route}\n"
        )

    def record(self, name: str, **kwargs) -> None:
        (self.sessions / f"rollout-{name}.jsonl").write_text(rollout(self.root, **kwargs))

    def collected(self) -> list:
        return audit.collect_sessions(self.root, self.sessions, self.authority)

    def run_compliance(self, baseline: Path | None = None) -> tuple[int, str]:
        stream = io.StringIO()
        with redirect_stdout(stream), redirect_stderr(stream):
            code = audit.compliance(
                self.root, self.authority, self.collected(), baseline or (self.root / "missing-baseline.json")
            )
        return code, stream.getvalue()

    def test_absent_history_is_not_a_violation(self) -> None:
        self.declare("FEAT-001", "reviewer-deep")
        argv = ["authority_audit.py", "--root", str(self.root), "--sessions-dir", str(self.sessions)]
        stream = io.StringIO()
        with patch.object(sys, "argv", argv), redirect_stdout(stream):
            code = audit.main()
        self.assertEqual(code, audit.EXIT_OK)
        self.assertIn("No history", stream.getvalue())

    def test_history_without_review_sessions_is_not_a_violation(self) -> None:
        self.declare("FEAT-001", "reviewer-deep")
        self.record("uat", role="uat", model=SUBAGENT, effort="medium", unit="FEAT-001", tokens=(10, 5, 1))
        code, output = self.run_compliance()
        self.assertEqual(code, audit.EXIT_OK)
        self.assertIn("No history: no review sessions recorded", output)

    def test_role_running_below_its_declared_authority_fails(self) -> None:
        self.declare("FEAT-001", "reviewer-deep")
        self.record("ok", role="reviewer-deep", model=ELEVATED, effort="high", unit="FEAT-001", tokens=(9, 4, 2))
        self.record("bad", role="reviewer-standard", model=SUBAGENT, effort="medium", unit=None, tokens=(9, 4, 2))
        code, output = self.run_compliance()
        self.assertEqual(code, audit.EXIT_VIOLATION)
        self.assertIn("[authority]", output)
        self.assertIn(f"reviewer-standard ran {SUBAGENT}/medium, declared {SUBAGENT}/high", output)

    def test_unit_reviewed_by_the_wrong_agent_fails(self) -> None:
        self.declare("FEAT-002", "reviewer-deep")
        self.record("cheap", role="reviewer-standard", model=SUBAGENT, effort="high", unit="FEAT-002", tokens=(9, 4, 2))
        code, output = self.run_compliance()
        self.assertEqual(code, audit.EXIT_VIOLATION)
        self.assertIn("[route]", output)
        self.assertIn("FEAT-002 declared reviewer-deep but was reviewed by reviewer-standard", output)

    def test_compliant_history_passes_and_reports_coverage(self) -> None:
        self.declare("FEAT-001", "reviewer-standard")
        self.declare("FEAT-002", "reviewer-deep")
        self.record("one", role="reviewer-standard", model=SUBAGENT, effort="high", unit="FEAT-001", tokens=(9, 4, 2))
        code, output = self.run_compliance()
        self.assertEqual(code, audit.EXIT_OK)
        self.assertIn("Every review session ran at its declared authority.", output)
        self.assertIn("No attributable review session for: FEAT-002", output)

    def test_baseline_suppresses_only_its_recorded_gaps(self) -> None:
        self.declare("FEAT-001", "reviewer-deep")
        self.record("bad", role="reviewer-deep", model=SUBAGENT, effort="medium", unit="FEAT-001", tokens=(9, 4, 2))
        baseline = self.root / "baseline.json"
        baseline.write_text(
            json.dumps(
                {
                    "max_entries": 1,
                    "accepted_violations": [
                        {
                            "kind": "authority",
                            "subject": "reviewer-deep",
                            "role": "reviewer-deep",
                            "observed": f"{SUBAGENT}/medium",
                            "reason": "accepted for this fixture",
                        }
                    ],
                }
            )
        )
        code, output = self.run_compliance(baseline)
        self.assertEqual(code, audit.EXIT_OK)
        self.assertIn("1 violation(s) accepted by baseline.json", output)

        self.record("other", role="reviewer-standard", model=ELEVATED, effort="low", unit=None, tokens=(1, 1, 1))
        code, output = self.run_compliance(baseline)
        self.assertEqual(code, audit.EXIT_VIOLATION)
        self.assertIn("reviewer-standard ran", output)

    def test_uninstantiated_authority_table_is_a_configuration_error(self) -> None:
        self.instantiate_authority(placeholders=True)
        self.declare("FEAT-001", "reviewer-deep")
        self.record("any", role="reviewer-deep", model="whatever", effort="high", unit="FEAT-001", tokens=(1, 1, 1))
        argv = ["authority_audit.py", "--root", str(self.root), "--sessions-dir", str(self.sessions)]
        stream = io.StringIO()
        with patch.object(sys, "argv", argv), redirect_stdout(stream), redirect_stderr(stream):
            code = audit.main()
        self.assertEqual(code, audit.EXIT_CONFIGURATION)
        self.assertIn("still holds placeholder model", stream.getvalue())

    def test_attribution_is_exact_or_absent(self) -> None:
        self.declare("FEAT-001", "reviewer-standard")
        self.declare("FEAT-002", "reviewer-standard")
        # A session that merely reads records is unattributed, never matched to
        # every record it happened to mention.
        (self.sessions / "rollout-mentions.jsonl").write_text(
            rollout(self.root, "reviewer-standard", SUBAGENT, "high", None, (9, 4, 2))
            + json.dumps({"type": "response_item", "payload": {"type": "message", "text": "read FEAT-001.md first"}})
            + "\n"
        )
        (self.sessions / "rollout-assigned.jsonl").write_text(
            rollout(self.root, "reviewer-standard", SUBAGENT, "high", "FEAT-002", (9, 4, 2))
            + json.dumps({"type": "response_item", "payload": {"type": "message", "text": "compared with FEAT-001.md"}})
            + "\n"
        )
        self.assertEqual([session.unit for session in self.collected()], ["FEAT-002", ""])

    def test_usage_rolls_up_tokens_by_role_and_by_unit(self) -> None:
        self.declare("FEAT-001", "reviewer-deep")
        self.record("review", role="reviewer-deep", model=ELEVATED, effort="high", unit="FEAT-001", tokens=(100, 60, 7))
        self.record("uat", role="uat", model=SUBAGENT, effort="medium", unit="FEAT-001", tokens=(40, 20, 3))
        self.record("loose", role="", model=ELEVATED, effort="medium", unit=None, tokens=(5, 1, 1))
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = audit.usage(self.collected())
        output = stream.getvalue()
        self.assertEqual(code, audit.EXIT_OK)
        self.assertIn("By role", output)
        self.assertIn("By unit", output)
        row = next(line for line in output.splitlines() if "FEAT-001" in line)
        self.assertEqual(row.split()[1:], ["2", "140", "80", "10"])
        self.assertIn("(unattributed)", output)
        self.assertIn("(primary)", output)


if __name__ == "__main__":
    unittest.main()
