from __future__ import annotations

import importlib.util
import re
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
    def packet(self, fixture: str, phase: str = "build", budget: int = 4000) -> str:
        relative = str((FIXTURES / fixture).relative_to(ROOT))
        return router.build_packet(ROOT, phase, feature=relative, budget=budget)

    def release_packet(self, budget: int = 4000) -> str:
        relative = str((FIXTURES / "release-record.md").relative_to(ROOT))
        return router.build_packet(ROOT, "release", release=relative, budget=budget)

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

    def test_rows_match_the_label_not_the_body(self) -> None:
        # Matching the whole row let a term like `Build` hit every row that
        # merely mentioned building, displacing real context with noise.
        lines = [
            "| Purpose | Command | Notes |",
            "| --- | --- | --- |",
            "| Build | `make build` | compile |",
            "| Deployment | `make ship` | run after the build completes |",
        ]
        matched = router.matching_rows(lines, ("Build",))
        self.assertEqual([index for index, _ in matched], [3])
        self.assertIn("make build", matched[0][1])
        self.assertNotIn("make ship", "".join(line for _, line in matched))

    def test_required_blocks_never_consume_the_supplementary_budget(self) -> None:
        # A phase with a large mandatory record used to lose all of its
        # supporting standards, because required and supplementary content were
        # charged against one budget.
        supporting = router.Block("CLEAN_CODE.md", "Project-Specific Additions", ((1, "- rule"),))
        small = router.Block("small.md", "record", ((1, "x"),), True)
        large = router.Block("large.md", "record", tuple((index, "y" * 100) for index in range(1, 60)), True)

        lean = router.render_packet("review", ROOT, [small, supporting], 4000)
        heavy = router.render_packet("review", ROOT, [large, supporting], 4000)
        for packet in (lean, heavy):
            self.assertIn("- rule", packet)
            self.assertNotIn("Omitted by packet budget", packet)
        self.assertGreater(len(heavy), len(lean))

    def test_supplementary_excerpt_must_beat_reading_the_whole_source(self) -> None:
        source = ROOT / "ARCHITECTURE.md"
        whole = router.read_lines(source)
        expensive = router.Block("ARCHITECTURE.md", "nearly the whole file", tuple(enumerate(whole, start=1)))
        packet = router.render_packet("build", ROOT, [expensive], 100000)
        self.assertIn("saves too little to ship", packet)
        self.assertIn("ARCHITECTURE.md:1-", packet)

    def test_every_packet_ends_with_its_spend_and_names_what_it_dropped(self) -> None:
        full = self.packet("agentic-ai.md", phase="review")
        self.assertIn("=== packet accounting ===", full)
        self.assertIn("phase subject matter, always emitted and never metered", full)
        self.assertRegex(full, r"Supplementary: \d+ of \d+ blocks shipped, \d+ of 4000 chars spent\.")
        self.assertNotIn("WARNING", full)

        starved = self.packet("agentic-ai.md", phase="review", budget=1000)
        self.assertIn("WARNING", starved)
        self.assertIn("supplementary block(s) omitted", starved)
        warning = starved.split("WARNING", 1)[1]
        self.assertIn("ARCHITECTURE.md:", warning)
        self.assertRegex(warning, r"— \d+ chars \(supplementary budget exhausted")

    def test_release_packet_routes_canonical_readiness_context(self) -> None:
        packet = self.release_packet()
        for contract in (
            "release record metadata",
            "Frozen MVP and Checklist Snapshot",
            "Supported Platform and Runtime Claims",
            "Deterministic Release Commands and Cases",
            "latest readiness and rework cycles",
            "Readiness Cycle 2",
            "Rework Cycle 1",
            "Separate Approval Authorities",
            "MVP.md",
            "Release Readiness",
            "Release Approval",
            "release command rows",
            "current-status documentation",
        ):
            self.assertIn(contract, packet)
        self.assertNotIn("### Readiness Cycle 1", packet)
        # The record under review is required subject matter and is never
        # metered; only the supplementary set answers to the budget.
        self.assertIn("Required:", packet)
        spent = int(re.search(r"(\d+) of (\d+) chars spent", packet).group(1))
        self.assertLessEqual(spent, 4000)

    def test_release_packet_budget_keeps_source_indexes(self) -> None:
        packet = self.release_packet(budget=1000)
        self.assertIn("release record metadata", packet)
        self.assertIn("Omitted by packet budget", packet)
        self.assertIn("release-record.md:", packet)
        self.assertIn("MVP.md:", packet)
        self.assertIn("ARCHITECTURE.md:", packet)

    def test_release_cli_accepts_only_the_canonical_record_path(self) -> None:
        fixture = str((FIXTURES / "release-record.md").relative_to(ROOT))
        argv = ["context_router.py", "release", "--root", str(ROOT), "--release", fixture]
        with patch.object(sys, "argv", argv):
            with self.assertRaisesRegex(SystemExit, "canonical record docs/releases/MVP-RELEASE.md"):
                router.main()


if __name__ == "__main__":
    unittest.main()
