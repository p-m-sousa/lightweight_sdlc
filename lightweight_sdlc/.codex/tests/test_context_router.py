from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
ROUTER_PATH = ROOT / ".codex/scripts/context_router.py"
SPEC = importlib.util.spec_from_file_location("context_router", ROUTER_PATH)
assert SPEC and SPEC.loader
router = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = router
SPEC.loader.exec_module(router)
FIXTURES = ROOT / ".codex/tests/fixtures"


class ContextRouterTests(unittest.TestCase):
    def packet(self, fixture: str, phase: str = "build", budget: int = 6000) -> str:
        relative = str((FIXTURES / fixture).relative_to(ROOT))
        return router.build_packet(ROOT, phase, feature=relative, budget=budget)

    def test_profile_sensitive_sections(self) -> None:
        web = self.packet("web-ui.md")
        agentic = self.packet("agentic-ai.md")
        ios = self.packet("ios.md")
        self.assertIn("DESIGN_SYSTEM.md", web)
        self.assertNotIn("External Integrations", web)
        self.assertIn("External Integrations", agentic)
        self.assertIn("DESIGN_SYSTEM.md", agentic)
        self.assertIn("DESIGN_SYSTEM.md", ios)
        self.assertIn("Module Map", ios)

    def test_budget_omits_optional_blocks_with_references(self) -> None:
        packet = self.packet("agentic-ai.md", budget=1000)
        self.assertIn("Acceptance Criteria and Cases", packet)
        self.assertIn("Omitted by packet budget", packet)
        self.assertIn("ARCHITECTURE.md:", packet)

    def test_latest_acceptance_and_rework_only(self) -> None:
        packet = self.packet("web-ui.md", phase="uat")
        self.assertIn("Acceptance Cycle 2", packet)
        self.assertIn("Rework Cycle 1", packet)
        self.assertNotIn("### Acceptance Cycle 1", packet)

    def test_representative_packets_earn_their_keep(self) -> None:
        results = []
        for fixture in ("web-ui.md", "agentic-ai.md", "ios.md"):
            packet = self.packet(fixture)
            tags = router.feature_fields(router.read_lines(FIXTURES / fixture))[1]
            source_paths = [FIXTURES / fixture, ROOT / "ARCHITECTURE.md", ROOT / "CLEAN_CODE.md"]
            if tags & {"web-ui", "ios"}:
                source_paths.append(ROOT / "DESIGN_SYSTEM.md")
            direct_context = sum(len(path.read_text()) for path in source_paths)
            results.append(len(packet) <= direct_context * 0.70)
        self.assertGreaterEqual(sum(results), 2)

    def test_git_state_distinguishes_unavailable_clean_and_changed(self) -> None:
        unavailable = subprocess.CompletedProcess([], 1, "", "not a repository")
        with patch.object(router.subprocess, "run", return_value=unavailable):
            self.assertEqual(router.git_state(ROOT), ("unavailable", []))

        clean_results = [subprocess.CompletedProcess([], 0, "true\n", "")] + [
            subprocess.CompletedProcess([], 0, "", "") for _ in range(3)
        ]
        with patch.object(router.subprocess, "run", side_effect=clean_results):
            self.assertEqual(router.git_state(ROOT), ("clean", []))

        changed_results = [
            subprocess.CompletedProcess([], 0, "true\n", ""),
            subprocess.CompletedProcess([], 0, "src/app.ts\n", ""),
            subprocess.CompletedProcess([], 0, "", ""),
            subprocess.CompletedProcess([], 0, "tests/app.test.ts\n", ""),
        ]
        with patch.object(router.subprocess, "run", side_effect=changed_results):
            self.assertEqual(router.git_state(ROOT), ("changed", ["src/app.ts", "tests/app.test.ts"]))

    def test_missing_optional_file_is_safe(self) -> None:
        self.assertEqual(router.read_lines(ROOT / "missing-design-file.md"), [])


if __name__ == "__main__":
    unittest.main()
