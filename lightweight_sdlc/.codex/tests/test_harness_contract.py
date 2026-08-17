from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    tomllib = None


ROOT = Path(__file__).resolve().parents[2]
DELEGATED_ROLES = ("planner", "reviewer-standard", "reviewer-deep", "uat", "architect")


class HarnessContractTests(unittest.TestCase):
    def load_toml(self, relative: str) -> dict:
        self.assertIsNotNone(tomllib, "Python 3.11+ is required to validate TOML contracts")
        with (ROOT / relative).open("rb") as handle:
            return tomllib.load(handle)

    def authority(self) -> dict:
        return self.load_toml(".codex/authority.toml")

    def test_configuration_and_dynamic_routing(self) -> None:
        authority = self.authority()
        config = self.load_toml(".codex/config.toml")
        self.assertEqual(config["model"], authority["models"]["primary"])
        self.assertEqual(config["model_reasoning_effort"], "medium")
        self.assertEqual(config["plan_mode_reasoning_effort"], "high")
        self.assertEqual(config["agents"]["default_subagent_model"], authority["models"]["subagent"])
        self.assertNotIn("max_threads", config["agents"])
        self.assertNotEqual(config.get("service_tier"), "fast")

    def test_delegated_authority_is_pinned_in_every_agent_definition(self) -> None:
        # Inverted deliberately. This assertion previously required `model` and
        # `model_reasoning_effort` to be ABSENT from the role definitions, which
        # made the runtime default the real authority and made the documented
        # review route unenforceable: effort was chosen per spawn from prose, so
        # a forgotten attribute produced a cheaper review that looked identical
        # to a correct one. Authority now belongs to the definition, and this
        # test pins the exact expected value per role.
        authority = self.authority()
        models = authority["models"]
        for name in DELEGATED_ROLES:
            declared = authority["roles"][name]
            role = self.load_toml(f".codex/agents/{name}.toml")
            self.assertEqual(role["name"], name, f"{name} definition must declare its own agent name")
            self.assertEqual(
                role["model"],
                models[declared["model"]],
                f"{name} must pin the model declared for it in .codex/authority.toml",
            )
            self.assertEqual(
                role["model_reasoning_effort"],
                declared["effort"],
                f"{name} must pin the reasoning effort declared for it in .codex/authority.toml",
            )
            self.assertIn("tool_output_token_limit", role)

    def test_authority_levels_are_separate_agents_with_identical_behavior(self) -> None:
        # Routing by agent name replaces "one agent plus a remembered override".
        # The two definitions may differ only in authority, so behavior cannot
        # drift between the profiles that select them.
        authority = self.authority()
        agents = set(authority["routes"]["review"].values())
        self.assertEqual(agents, {"reviewer-standard", "reviewer-deep"})
        standard = self.load_toml(".codex/agents/reviewer-standard.toml")
        deep = self.load_toml(".codex/agents/reviewer-deep.toml")
        self.assertEqual(
            standard["developer_instructions"],
            deep["developer_instructions"],
            "review agents must be byte-identical in behavior; only authority may differ",
        )
        self.assertEqual(standard["sandbox_mode"], deep["sandbox_mode"])
        self.assertEqual(standard["tool_output_token_limit"], deep["tool_output_token_limit"])
        self.assertNotEqual(standard["model"], deep["model"])
        self.assertFalse((ROOT / ".codex/agents/reviewer.toml").exists(), "the overridable single reviewer is gone")

    def test_process_documents_name_agents_not_models_or_efforts(self) -> None:
        # A model named in prose is drift waiting to happen: the prose and the
        # definition diverge silently, and the definition is what actually runs.
        authority = self.authority()
        patterns = [re.compile(pattern) for pattern in authority["document_guard"]["forbidden_patterns"]]
        placeholders = [re.escape(value) for value in authority["models"].values()]
        patterns.append(re.compile("|".join(placeholders)))
        for relative in authority["document_guard"]["documents"]:
            content = (ROOT / relative).read_text()
            for pattern in patterns:
                found = pattern.search(content)
                self.assertIsNone(
                    found,
                    f"{relative} names an authority identifier {found.group(0)!r}; name the agent instead"
                    if found
                    else "",
                )

    def test_prompt_size_guardrails(self) -> None:
        self.assertLessEqual(len((ROOT / "AGENTS.md").read_text()), 6000)
        ceilings = {"planner": 2400, "reviewer-standard": 3000, "reviewer-deep": 3000, "uat": 3000, "architect": 8000}
        for name, ceiling in ceilings.items():
            instructions = self.load_toml(f".codex/agents/{name}.toml")["developer_instructions"]
            self.assertLessEqual(len(instructions), ceiling, f"{name} prompt exceeds its ceiling")

    def test_sections_injected_into_every_packet_stay_capped(self) -> None:
        # These sections bypass the packet budget, so every delivery turn in
        # every phase that routes them pays for them. Operational detail belongs
        # in a document the packet points at, not in a section it pastes.
        ceilings = {
            ("PRODUCT_VISION.md", "North Star"): 400,
            ("PRODUCT_VISION.md", "Trust Promise"): 600,
            ("PRODUCT_VISION.md", "Decision Filter"): 900,
            ("MVP.md", "MVP Outcome"): 500,
        }
        for (relative, heading), ceiling in ceilings.items():
            content = (ROOT / relative).read_text()
            match = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", content, re.MULTILINE | re.DOTALL)
            self.assertIsNotNone(match, f"{relative} lost its {heading} section")
            size = len(match.group(0))
            self.assertLessEqual(
                size,
                ceiling,
                f"{relative} :: {heading} is {size} chars against a {ceiling} ceiling. This section is injected"
                " into every packet that routes it and is paid on every delivery turn; move the operational"
                f" detail into a document the packet points at and leave a short statement in {relative}.",
            )

    def test_authority_baseline_is_explicit_and_shrink_only(self) -> None:
        baseline = json.loads((ROOT / ".codex/authority_baseline.json").read_text())
        entries = baseline["accepted_violations"]
        cap = baseline["max_entries"]  # the cap derives from the file, never a literal count
        self.assertGreaterEqual(cap, 0)
        self.assertLessEqual(len(entries), cap, "baseline grew past its own declared cap")
        self.assertEqual(
            len(entries),
            cap,
            "ratchet max_entries down to the gaps actually accepted; raising it must be an explicit, reviewable edit",
        )
        for entry in entries:
            self.assertEqual({"kind", "subject", "role", "observed", "reason"}, set(entry))
        # Distribution-only: an adopting project that accepts a real gap edits
        # this assertion in the same reviewable change. Never seed the shipped
        # baseline with any project's history.
        self.assertEqual(entries, [], "the distributed baseline ships empty")

    def test_authority_audit_harvests_existing_logs_without_new_instrumentation(self) -> None:
        authority = self.authority()
        audit = (ROOT / ".codex/scripts/authority_audit.py").read_text()
        self.assertIn("directory", authority["sessions"])
        self.assertIn("glob", authority["sessions"])
        self.assertIn("review_roles", authority["audit"])
        self.assertIn("agent_role", audit)
        self.assertIn("total_token_usage", audit)
        for mode in ("compliance", "usage"):
            self.assertIn(mode, audit)

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
        self.assertIn("reviewer-standard", kanban)
        self.assertIn("reviewer-deep", kanban)

    def test_removed_review_artifacts_have_no_references(self) -> None:
        forbidden = ("docs/code-reviews", "triage-log.md", "review archive")
        for path in ROOT.rglob("*.md"):
            if ".codex/tests/fixtures" in str(path):
                continue
            content = path.read_text(errors="replace").casefold()
            for value in forbidden:
                self.assertNotIn(value.casefold(), content, f"stale review artifact reference in {path}")

    def test_example_routes(self) -> None:
        routes = self.authority()["routes"]["review"]
        expected = {
            "web-ui.md": ("standard", "builder", "reviewer-standard", "independent-uat"),
            "agentic-ai.md": ("deep", "delegated", "reviewer-deep", "independent-uat"),
            "ios.md": ("deep", "delegated", "reviewer-deep", "independent-uat"),
        }
        for fixture, values in expected.items():
            content = (ROOT / ".codex/tests/fixtures" / fixture).read_text()
            for value in values:
                self.assertIn(value, content)
            self.assertIn(values[2], routes, "every example review route must resolve through the route table")

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

        for name in DELEGATED_ROLES:
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

    def test_test_execution_uses_environment_derived_guardrails(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text()
        architecture = (ROOT / "ARCHITECTURE.md").read_text()
        uat = self.load_toml(".codex/agents/uat.toml")["developer_instructions"]
        guard = ROOT / ".codex/scripts/test_guard.py"

        self.assertTrue(guard.is_file())
        self.assertIn("test_guard.py", agents)
        self.assertIn("bounded fallback rather than block testing", agents)
        self.assertIn("Codex approval", agents)
        self.assertIn("Guarded command", architecture)
        self.assertIn("test_guard.py", architecture)
        self.assertIn("test_guard.py", uat)
        self.assertIn("approved override", uat)

    def test_done_automatically_triggers_release_eligibility(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text()
        kanban = (ROOT / "KANBAN.md").read_text()
        self.assertIn("After every active-MVP Done, automatically apply", agents)
        self.assertIn("After every active-MVP capability reaches Done, immediately evaluate release eligibility", kanban)
        self.assertIn("do not wait for another user prompt", kanban)
        self.assertIn("all included capabilities are Done with reviewed passing acceptance", kanban)
        self.assertIn("automatically enter Release Readiness", kanban)

    def test_canonical_release_record_contract_and_identity(self) -> None:
        template = (ROOT / "docs/releases/TEMPLATE.md").read_text()
        kanban = (ROOT / "KANBAN.md").read_text()
        for contract in (
            "Record kind: `harness-owned release readiness`",
            "Canonical path: `docs/releases/MVP-RELEASE.md`",
            "## Frozen MVP and Checklist Snapshot",
            "## Supported Platform and Runtime Claims",
            "## Deterministic Release Commands and Cases",
            "## Readiness and Rework Cycles",
            "## Independent Evidence Review",
            "## Separate Approval Authorities",
            "Declared core smoke check: `RR-002`",
        ):
            self.assertIn(contract, template)
        for check in range(1, 15):
            self.assertGreaterEqual(template.count(f"RR-{check:03d}"), 2, "check must appear in snapshot and cycle table")
        self.assertIn("create `docs/releases/MVP-RELEASE.md`", kanban)
        self.assertIn("otherwise resume it", kanban)
        self.assertIn("one canonical harness-owned record", kanban)
        self.assertFalse((ROOT / "docs/releases/MVP-RELEASE.md").exists(), "distribution must not invent a live release record")
        self.assertEqual([path.name for path in (ROOT / "docs/releases").glob("*.md")], ["TEMPLATE.md"])
        for forbidden in ("# [FEATURE-ID]", "Source backlog item:", "Delivery profile:", "Acceptance route:"):
            self.assertNotIn(forbidden, template)
        self.assertIn("never receives a feature ID, backlog row, Kanban card", template)

    def test_release_checks_have_closed_status_and_evidence_contracts(self) -> None:
        template = (ROOT / "docs/releases/TEMPLATE.md").read_text()
        status_line = next(line for line in template.splitlines() if "Every check row must use exactly" in line)
        self.assertEqual(set(re.findall(r"`([^`]+)`", status_line)), {"pending", "pass", "fail", "blocked", "n/a"})
        for requirement in (
            "reproducible command or black-box case",
            "date",
            "exact environment",
            "evidence reference",
            "owner/next action",
            "`n/a` also requires a concrete reason",
            "Missing evidence is never a pass",
        ):
            self.assertIn(requirement, template)

    def test_release_cycles_preserve_evidence_and_prepare_remediation(self) -> None:
        template = (ROOT / "docs/releases/TEMPLATE.md").read_text()
        kanban = (ROOT / "KANBAN.md").read_text()
        for contract in (
            "never overwrite or delete a completed, failed, or blocked cycle",
            "#### Prepared Product Decisions",
            "Failed Check ID",
            "Proposed Remediation Scope",
            "Recommended Backlog Item",
            "Do not create the backlog item, feature record, MVP capability, or implementation",
            "Affected checks to rerun",
            "Required core smoke: `RR-002`",
            "Broad-suite trigger",
        ):
            self.assertIn(contract, template)
        self.assertIn("Never edit away failed or blocked cycles", kanban)
        self.assertIn("link its record from the release Rework Cycle", kanban)
        self.assertIn("resume readiness automatically after it reaches Done", kanban)

    def test_release_authorities_are_explicit_and_independent(self) -> None:
        template = (ROOT / "docs/releases/TEMPLATE.md").read_text()
        mvp = (ROOT / "MVP.md").read_text()
        authorities = (
            "Feature Done approval(s):",
            "Commit authorization:",
            "Live or cost-bearing UAT authorization:",
            "Ready-for-release-review determination:",
            "Final MVP release approval:",
            "Publish/deploy authorization:",
        )
        for authority in authorities:
            self.assertIn(authority, template)
            self.assertIn(authority, mvp)
        self.assertIn("No value, transition, or approval in one field grants or implies any other", template)
        self.assertIn("Never mark this MVP Released without the user's separate explicit", mvp)
        self.assertIn("Never publish or deploy without separate", mvp)

    def test_release_work_continues_until_a_real_authority_boundary(self) -> None:
        kanban = (ROOT / "KANBAN.md").read_text()
        for automatic_work in (
            "evidence mapping",
            "documentation consistency checks",
            "deterministic release tooling",
            "applicable guarded validation",
        ):
            self.assertIn(automatic_work, kanban)
        for boundary in (
            "material product/MVP/design/scope decision",
            "cost authorization",
            "permission",
            "credential",
            "safety decision",
            "destructive action",
            "unavailable environment",
        ):
            self.assertIn(boundary, kanban)
        self.assertIn("Only reviewed passing release evidence permits", kanban)
        self.assertIn("separate explicit Final MVP release approval", kanban)


if __name__ == "__main__":
    unittest.main()
