from __future__ import annotations

import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    tomllib = None


ROOT = Path(__file__).resolve().parents[2]


class HarnessContractTests(unittest.TestCase):
    def load_toml(self, relative: str) -> dict:
        self.assertIsNotNone(tomllib, "Python 3.11+ is required to validate TOML contracts")
        with (ROOT / relative).open("rb") as handle:
            return tomllib.load(handle)

    def test_configuration_and_dynamic_routing(self) -> None:
        config = self.load_toml(".codex/config.toml")
        self.assertEqual(config["model"], "gpt-5.6-sol")
        self.assertEqual(config["model_reasoning_effort"], "medium")
        self.assertEqual(config["plan_mode_reasoning_effort"], "high")
        self.assertEqual(config["agents"]["default_subagent_model"], "gpt-5.6-terra")
        self.assertNotIn("max_threads", config["agents"])
        self.assertNotEqual(config.get("service_tier"), "fast")

        for name in ("planner", "reviewer", "uat"):
            role = self.load_toml(f".codex/agents/{name}.toml")
            self.assertNotIn("model", role)
            self.assertNotIn("model_reasoning_effort", role)
            self.assertIn("tool_output_token_limit", role)
        architect = self.load_toml(".codex/agents/architect.toml")
        self.assertEqual(architect["model_reasoning_effort"], "high")

    def test_prompt_size_guardrails(self) -> None:
        self.assertLessEqual(len((ROOT / "AGENTS.md").read_text()), 6000)
        ceilings = {"planner": 2400, "reviewer": 3000, "uat": 3000, "architect": 8000}
        for name, ceiling in ceilings.items():
            instructions = self.load_toml(f".codex/agents/{name}.toml")["developer_instructions"]
            self.assertLessEqual(len(instructions), ceiling, f"{name} prompt exceeds its ceiling")

    def test_single_feature_record_contract(self) -> None:
        template = (ROOT / "docs/features/TEMPLATE.md").read_text()
        for field in (
            "Delivery profile:", "Surface tags:", "Planning route:", "Review route:", "Acceptance route:",
            "## Review Cycles", "## Acceptance and Rework Cycles", "## Efficiency and Final Disposition",
            "Focused reviewer verdict:", "Done:", "Canceled:", "MVP update",
            "README impact:",
        ):
            self.assertIn(field, template)
        self.assertNotIn("docs/code-reviews", template)

    def test_canonical_lifecycle_states(self) -> None:
        for relative in ("KANBAN.md", "docs/features/TEMPLATE.md", "README.md"):
            content = (ROOT / relative).read_text()
            for state in ("Building", "Testing", "Done", "Canceled"):
                self.assertIn(state, content, f"{state} missing from {relative}")
        kanban = (ROOT / "KANBAN.md").read_text()
        self.assertIn('fork_turns="none"', kanban)
        self.assertIn("Terra High", kanban)
        self.assertIn("Sol High", kanban)

    def test_removed_review_artifacts_have_no_references(self) -> None:
        forbidden = ("docs/code-reviews", "triage-log.md", "review archive")
        for path in ROOT.rglob("*.md"):
            if ".codex/tests/fixtures" in str(path):
                continue
            content = path.read_text(errors="replace").casefold()
            for value in forbidden:
                self.assertNotIn(value.casefold(), content, f"stale review artifact reference in {path}")

    def test_example_routes(self) -> None:
        expected = {
            "web-ui.md": ("standard", "builder", "terra-high", "independent-uat"),
            "agentic-ai.md": ("deep", "delegated", "sol-high", "independent-uat"),
            "ios.md": ("deep", "delegated", "sol-high", "independent-uat"),
        }
        for fixture, values in expected.items():
            content = (ROOT / ".codex/tests/fixtures" / fixture).read_text()
            for value in values:
                self.assertIn(value, content)

    def test_product_owner_creates_project_readme_after_architecture(self) -> None:
        skill = (ROOT / ".agents/skills/product-owner/SKILL.md").read_text()
        self.assertIn("## Project README", skill)
        self.assertIn("After a completed bootstrap architecture pass", skill)
        self.assertIn("exact setup, local-run, focused-validation", skill)
        self.assertIn("Lightweight SDLC Agent Workflow", skill)
        self.assertIn("needs no separate draft approval", skill)
        self.assertIn("treat README as living project documentation", skill)
        self.assertIn("Every feature record states the README impact", skill)

    def test_product_owner_refines_in_flight_products_proportionally(self) -> None:
        skill = (ROOT / ".agents/skills/product-owner/SKILL.md").read_text()
        metadata = (ROOT / ".agents/skills/product-owner/agents/openai.yaml").read_text()
        agents = (ROOT / "AGENTS.md").read_text()
        readme = (ROOT / "README.md").read_text()
        architect = self.load_toml(".codex/agents/architect.toml")

        for contract in (
            "**In-flight refinement:**",
            "classify it before drafting",
            "**No product change:**",
            "**Backlog refinement:**",
            "Building, Testing, Done, or active MVP",
            "Done remains historical truth",
            "only the complete affected section",
            "invoke Architect only when",
            "skip it with a concise reason",
        ):
            self.assertIn(contract, skill)
        self.assertIn("refine", metadata)
        self.assertIn("architecture-relevant approved refinement", architect["description"])
        self.assertIn("Architect receives its role-defined product handoff", agents)
        continuation = "Write the approved product changes and complete the product handoff."
        self.assertIn(continuation, skill)
        self.assertIn(continuation, readme)
        self.assertNotIn("Write the approved product changes and continue to architecture.", readme)
        self.assertNotIn("separate refinement skill", skill.casefold())

    def test_product_owner_requires_thin_backlog_slices_in_all_modes(self) -> None:
        skill = (ROOT / ".agents/skills/product-owner/SKILL.md").read_text()
        for contract in (
            "thinnest coherent vertical slice",
            "bootstrap, refinement, rescope, and new-feature discovery",
            "one observable outcome for one primary actor or journey",
            "can be prioritized, implemented, reviewed, and accepted independently",
            "state why each candidate cannot be sliced thinner",
            "do not hide later slices inside acceptance language or Notes",
        ):
            self.assertIn(contract, skill)

    def test_delegated_roles_fail_fast_without_requesting_tool_approval(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text()
        kanban = (ROOT / "KANBAN.md").read_text()
        self.assertIn("Delegates never install or request tool approval", agents)
        self.assertIn("immediately return the exact `blocked` condition", agents)
        self.assertIn("If planning is blocked, leave the item in Backlog", kanban)
        self.assertIn("If review is blocked, remain in Building", kanban)

        for name in ("planner", "reviewer", "uat", "architect"):
            instructions = self.load_toml(f".codex/agents/{name}.toml")["developer_instructions"]
            for contract in (
                "preflight the tools, dependencies, permissions, credentials",
                "Never install dependencies or issue a tool approval request",
                "no equivalent in-scope workaround exists",
                "stop immediately",
            ):
                self.assertIn(contract, instructions, f"{name} lacks fail-fast contract")
            self.assertIn("blocked", instructions.casefold())

        planner = self.load_toml(".codex/agents/planner.toml")["developer_instructions"]
        self.assertIn("Verdict: ready | needs user decision | does not align | blocked", planner)


if __name__ == "__main__":
    unittest.main()
