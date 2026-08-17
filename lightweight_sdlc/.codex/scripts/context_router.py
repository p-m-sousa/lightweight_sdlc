#!/usr/bin/env python3
"""Emit a budgeted, current context packet for one lightweight-SDLC phase."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FIELD = re.compile(r"^-\s+([^:]+):\s*(.+?)\s*$")

# The budget meters supplementary blocks only. Required blocks are the phase's
# subject matter and always emit, so a large mandatory record can never crowd
# out the standards a phase needs.
DEFAULT_BUDGET = 4000

# A supplementary excerpt only earns its place when it costs materially less
# than an agent reading the whole source document. Above this share, shipping
# the excerpt buys nothing, so the packet points at the source instead.
MAX_EXCERPT_SHARE = 0.5


@dataclass(frozen=True)
class Block:
    path: str
    label: str
    content: tuple[tuple[int, str], ...]
    required: bool = False


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if all((candidate / name).is_file() for name in ("AGENTS.md", "KANBAN.md", "PRODUCT_VISION.md")):
            return candidate
    raise SystemExit("Could not find a harness project root from the current directory.")


def read_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("`")).casefold()


def section(lines: list[str], heading: str) -> list[tuple[int, str]]:
    wanted = normalize(heading)
    start: int | None = None
    level: int | None = None
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if match and normalize(match.group(2)) == wanted:
            start, level = index, len(match.group(1))
            break
    if start is None or level is None:
        return []
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = HEADING.match(lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return [(index + 1, lines[index]) for index in range(start, end)]


def preamble(lines: list[str]) -> list[tuple[int, str]]:
    end = next((index for index, line in enumerate(lines) if line.startswith("## ")), len(lines))
    return [(index + 1, lines[index]) for index in range(end)]


def row_label(line: str) -> str:
    """First cell of a table row: what the row is about, not what it mentions."""
    return normalize(line.strip().strip("|").split("|")[0])


def matching_rows(lines: list[str], terms: Iterable[str]) -> list[tuple[int, str]]:
    """Match routing terms against the row label only.

    Matching the whole row lets a term like `Build` hit every row that merely
    mentions building, pulling thousands of characters of unrelated context in
    place of the rows actually asked for.
    """
    wanted = tuple(normalize(term) for term in terms)
    return [
        (index + 1, line)
        for index, line in enumerate(lines)
        if line.lstrip().startswith("|") and any(term in row_label(line) for term in wanted)
    ]


def latest_subsections(lines: list[str], parent_heading: str, prefixes: tuple[str, ...]) -> list[tuple[int, str]]:
    parent = section(lines, parent_heading)
    if not parent:
        return []
    parent_match = HEADING.match(parent[0][1])
    if not parent_match:
        return parent
    parent_level = len(parent_match.group(1))
    children: list[tuple[int, int, str]] = []
    for offset, (_, line) in enumerate(parent[1:], start=1):
        match = HEADING.match(line)
        if match and len(match.group(1)) > parent_level:
            children.append((offset, len(match.group(1)), normalize(match.group(2))))
    intro_end = children[0][0] if children else len(parent)
    selected = list(parent[:intro_end])
    for prefix in prefixes:
        matches = [child for child in children if child[2].startswith(normalize(prefix))]
        if not matches:
            continue
        start, level, _ = matches[-1]
        end = len(parent)
        for offset in range(start + 1, len(parent)):
            match = HEADING.match(parent[offset][1])
            if match and len(match.group(1)) <= level:
                end = offset
                break
        selected.extend(parent[start:end])
    return sorted(dict(selected).items())


def contiguous_groups(content: tuple[tuple[int, str], ...]) -> list[tuple[tuple[int, str], ...]]:
    if not content:
        return []
    groups: list[list[tuple[int, str]]] = [[content[0]]]
    for entry in content[1:]:
        if entry[0] == groups[-1][-1][0] + 1:
            groups[-1].append(entry)
        else:
            groups.append([entry])
    return [tuple(group) for group in groups]


def render_group(path: str, label: str, group: tuple[tuple[int, str], ...]) -> str:
    start, end = group[0][0], group[-1][0]
    reference = f"{path}:{start}" if start == end else f"{path}:{start}-{end}"
    body = "\n".join(line for _, line in group)
    return f"\n=== {reference} :: {label} ===\n{body}\n"


def block_references(block: Block) -> str:
    references = []
    for group in contiguous_groups(block.content):
        start, end = group[0][0], group[-1][0]
        references.append(f"{block.path}:{start}" if start == end else f"{block.path}:{start}-{end}")
    return ", ".join(references)


def render_block(block: Block) -> str:
    return "".join(render_group(block.path, block.label, group) for group in contiguous_groups(block.content))


def render_omission(block: Block, cost: int, reason: str) -> str:
    if not block.content:
        return ""
    return (
        f"\n=== {block_references(block)} :: {block.label} ===\n"
        f"[Omitted by packet budget; {cost} chars, {reason}. Open the source when correctness requires it.]\n"
    )


def source_cost(root: Path, relative: str) -> int:
    """Cost of an agent reading the whole source document instead of the excerpt."""
    path = root / relative
    if not path.is_file():
        return 0
    return len(path.read_text(encoding="utf-8", errors="replace"))


def plan_supplementary(root: Path, blocks: list[Block], budget: int) -> tuple[dict[int, str], int]:
    """Choose which supplementary blocks ship, cheapest first.

    A block is dropped when its excerpt does not cost materially less than
    reading its whole source, or when the supplementary budget is spent. Only
    supplementary blocks are metered, so required context never displaces them.
    """
    dropped: dict[int, str] = {}
    spent = 0
    optional = [(index, block) for index, block in enumerate(blocks) if block.content and not block.required]
    costs = {index: len(render_block(block)) for index, block in optional}
    for index, block in sorted(optional, key=lambda entry: (costs[entry[0]], entry[0])):
        cost = costs[index]
        source = source_cost(root, block.path)
        if source and cost > source * MAX_EXCERPT_SHARE:
            dropped[index] = f"excerpt is {cost} of a {source}-char source and saves too little to ship"
        elif spent + cost > budget:
            dropped[index] = f"supplementary budget exhausted at {spent} of {budget} chars"
        else:
            spent += cost
    return dropped, spent


def render_accounting(required: list[int], optional_count: int, spent: int, budget: int, omitted: list[str]) -> str:
    lines = [
        "\n=== packet accounting ===",
        f"Required: {len(required)} blocks, {sum(required)} chars — phase subject matter, always emitted and never metered.",
        f"Supplementary: {optional_count - len(omitted)} of {optional_count} blocks shipped, {spent} of {budget} chars spent.",
    ]
    if omitted:
        lines.append(f"WARNING: {len(omitted)} supplementary block(s) omitted; open each source directly when correctness requires it:")
        lines.extend(f"  - {entry}" for entry in omitted)
    return "\n".join(lines) + "\n"


def render_packet(phase: str, root: Path, blocks: list[Block], budget: int) -> str:
    dropped, spent = plan_supplementary(root, blocks, budget)
    output = f"Context packet: {phase}\nRoot: {root}\nRead-only starting index; expand only when correctness requires it.\n"
    required: list[int] = []
    optional_count = 0
    omitted: list[str] = []
    for index, block in enumerate(blocks):
        if not block.content:
            continue
        rendered = render_block(block)
        if block.required:
            required.append(len(rendered))
            output += rendered
            continue
        optional_count += 1
        if index in dropped:
            output += render_omission(block, len(rendered), dropped[index])
            omitted.append(f"{block_references(block)} :: {block.label} — {len(rendered)} chars ({dropped[index]})")
        else:
            output += rendered
    return output.rstrip() + "\n" + render_accounting(required, optional_count, spent, budget, omitted)


def add_section(blocks: list[Block], root: Path, relative: str, heading: str, *, required: bool = False) -> None:
    content = section(read_lines(root / relative), heading)
    if content:
        blocks.append(Block(relative, heading, tuple(content), required))


def resolve_record(root: Path, record: str, kind: str) -> tuple[Path, str, list[str]]:
    path = Path(record)
    if not path.is_absolute():
        path = root / path
    try:
        relative = str(path.relative_to(root))
    except ValueError as exc:
        raise SystemExit(f"{kind.capitalize()} record must be inside the project root.") from exc
    lines = read_lines(path)
    if not lines:
        raise SystemExit(f"{kind.capitalize()} record is missing or empty: {relative}")
    return path, relative, lines


def resolve_feature(root: Path, feature: str) -> tuple[Path, str, list[str]]:
    return resolve_record(root, feature, "feature")


def feature_fields(lines: list[str]) -> tuple[str, set[str]]:
    fields: dict[str, str] = {}
    for _, line in preamble(lines):
        match = FIELD.match(line)
        if match:
            fields[normalize(match.group(1))] = normalize(match.group(2))
    profile = fields.get("delivery profile", "deep")
    tags = {tag for tag in re.split(r"[\s,|/]+", fields.get("surface tags", "")) if tag}
    return profile, tags


def git_state(root: Path) -> tuple[str, list[str]]:
    probe = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return "unavailable", []
    commands = (
        ["git", "-C", str(root), "diff", "--name-only"],
        ["git", "-C", str(root), "diff", "--cached", "--name-only"],
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"],
    )
    paths: set[str] = set()
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return "unavailable", []
        paths.update(line.strip() for line in result.stdout.splitlines() if line.strip())
    return ("changed", sorted(paths)) if paths else ("clean", [])


def plan_blocks(root: Path, item: str) -> list[Block]:
    blocks: list[Block] = []
    backlog = read_lines(root / "BACKLOG.md")
    rows = matching_rows(backlog, (item,))
    blocks.append(Block("BACKLOG.md", f"rows matching {item!r}", tuple(rows), True))
    for heading in ("North Star", "Trust Promise", "Decision Filter"):
        add_section(blocks, root, "PRODUCT_VISION.md", heading, required=True)
    mvp = read_lines(root / "MVP.md")
    if mvp:
        blocks.append(Block("MVP.md", "status", tuple(preamble(mvp)), True))
        add_section(blocks, root, "MVP.md", "MVP Outcome", required=True)
        mvp_rows = matching_rows(mvp, (item,))
        if mvp_rows:
            blocks.append(Block("MVP.md", f"rows matching {item!r}", tuple(mvp_rows), True))
    for heading in ("Summary", "Structural Invariants"):
        add_section(blocks, root, "ARCHITECTURE.md", heading)
    commands = matching_rows(read_lines(root / "ARCHITECTURE.md"), ("Build", "Focused unit", "Feature-specific", "Rendered validation"))
    blocks.append(Block("ARCHITECTURE.md", "relevant command rows", tuple(commands)))
    return blocks


def feature_blocks(root: Path, feature: str, phase: str) -> list[Block]:
    _, relative, lines = resolve_feature(root, feature)
    profile, tags = feature_fields(lines)
    ui = bool(tags & {"web-ui", "ios"})
    agentic = "agentic-ai" in tags
    blocks: list[Block] = [Block(relative, "metadata and routing", tuple(preamble(lines)), True)]

    headings_by_phase = {
        "build": ("Scope and Plan", "Acceptance Criteria and Cases"),
        "review": ("Scope and Plan", "Acceptance Criteria and Cases", "Implementation and Validation", "Review Cycles"),
        "uat": ("Acceptance Criteria and Cases",),
    }
    for heading in headings_by_phase[phase]:
        content = section(lines, heading)
        if content:
            blocks.append(Block(relative, heading, tuple(content), True))

    if phase in {"review", "uat"}:
        recent = latest_subsections(lines, "Acceptance and Rework Cycles", ("Acceptance Cycle", "Rework Cycle"))
        if recent:
            blocks.append(Block(relative, "latest acceptance and rework", tuple(recent), True))

    if phase == "review":
        state, paths = git_state(root)
        summary = [f"state: {state}"] + paths
        blocks.append(Block("repository", "current changed files", tuple((index + 1, value) for index, value in enumerate(summary)), True))

    if phase in {"build", "review"}:
        for heading in ("Summary", "Structural Invariants"):
            add_section(blocks, root, "ARCHITECTURE.md", heading)
        command_terms = ("Build", "Format", "Lint", "Typecheck", "Focused unit", "Feature-specific")
        commands = matching_rows(read_lines(root / "ARCHITECTURE.md"), command_terms)
        blocks.append(Block("ARCHITECTURE.md", "relevant command rows", tuple(commands)))
        add_section(blocks, root, "CLEAN_CODE.md", "Project-Specific Additions")
    else:
        command_terms = ("Run locally", "Feature-specific end-to-end", "Rendered validation")
        commands = matching_rows(read_lines(root / "ARCHITECTURE.md"), command_terms)
        blocks.append(Block("ARCHITECTURE.md", "acceptance target and command rows", tuple(commands)))

    if agentic:
        add_section(blocks, root, "ARCHITECTURE.md", "External Integrations")
        add_section(blocks, root, "ARCHITECTURE.md", "Cross-Cutting Constraints")
    if ui:
        add_section(blocks, root, "DESIGN_SYSTEM.md", "Project-Specific Additions")
    if profile == "deep" and phase == "build":
        add_section(blocks, root, "ARCHITECTURE.md", "Module Map")
    return blocks


def release_blocks(root: Path, release: str) -> list[Block]:
    _, relative, lines = resolve_record(root, release, "release")
    blocks: list[Block] = [Block(relative, "release record metadata", tuple(preamble(lines)), True)]

    # The record under review is the phase's subject matter, exactly as the
    # feature record is for Build, Review, and UAT: required, never metered.
    for heading in (
        "Frozen MVP and Checklist Snapshot",
        "Supported Platform and Runtime Claims",
        "Deterministic Release Commands and Cases",
    ):
        content = section(lines, heading)
        if content:
            blocks.append(Block(relative, heading, tuple(content), True))

    recent = latest_subsections(lines, "Readiness and Rework Cycles", ("Readiness Cycle", "Rework Cycle"))
    if recent:
        blocks.append(Block(relative, "latest readiness and rework cycles", tuple(recent), True))
    for heading in ("Independent Evidence Review", "Separate Approval Authorities"):
        content = section(lines, heading)
        if content:
            blocks.append(Block(relative, heading, tuple(content), True))

    mvp = read_lines(root / "MVP.md")
    if mvp:
        blocks.append(Block("MVP.md", "active MVP metadata", tuple(preamble(mvp)), True))
        for heading in ("Release Readiness", "Release Approval"):
            content = section(mvp, heading)
            if content:
                blocks.append(Block("MVP.md", heading, tuple(content)))

    commands = matching_rows(
        read_lines(root / "ARCHITECTURE.md"),
        (
            "Setup",
            "Build",
            "Run locally",
            "Full automated regression",
            "Feature-specific end-to-end",
            "Full end-to-end regression",
            "Deterministic release/package",
            "Publish/deploy",
        ),
    )
    if commands:
        blocks.append(Block("ARCHITECTURE.md", "release command rows", tuple(commands)))

    readme = read_lines(root / "README.md")
    for heading in ("Current Status", "Status", "MVP Status", "Release Status"):
        content = section(readme, heading)
        if content:
            blocks.append(Block("README.md", "current-status documentation", tuple(content)))
            break
    return blocks


def build_packet(
    root: Path,
    phase: str,
    *,
    item: str | None = None,
    feature: str | None = None,
    release: str | None = None,
    budget: int = DEFAULT_BUDGET,
) -> str:
    if phase == "plan":
        if not item:
            raise ValueError("Plan requires an item.")
        blocks = plan_blocks(root, item)
    elif phase == "release":
        if not release:
            raise ValueError("Release requires a release record.")
        blocks = release_blocks(root, release)
    else:
        if not feature:
            raise ValueError(f"{phase.capitalize()} requires a feature.")
        blocks = feature_blocks(root, feature, phase)
    return render_packet(phase, root, blocks, budget)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("plan", "build", "review", "uat", "release"))
    parser.add_argument("--item", help="Exact backlog item name for Plan.")
    parser.add_argument("--feature", help="Feature-record path for Build, Review, or UAT.")
    parser.add_argument("--release", help="Harness-owned release-record path for Release.")
    parser.add_argument("--root", type=Path, help="Project root; defaults to discovery from the current directory.")
    parser.add_argument(
        "--budget-chars",
        type=int,
        default=DEFAULT_BUDGET,
        help="Soft character budget for supplementary blocks; required blocks are never metered.",
    )
    args = parser.parse_args()
    if args.phase == "plan" and not args.item:
        parser.error("Plan requires --item.")
    if args.phase in {"build", "review", "uat"} and not args.feature:
        parser.error(f"{args.phase.capitalize()} requires --feature.")
    if args.phase == "release" and not args.release:
        parser.error("Release requires --release.")
    if args.budget_chars < 1000:
        parser.error("--budget-chars must be at least 1000.")
    return args


def main() -> None:
    args = parse_args()
    root = args.root.resolve() if args.root else find_root(Path.cwd().resolve())
    if args.phase == "release":
        requested = Path(args.release)
        requested = requested.resolve() if requested.is_absolute() else (root / requested).resolve()
        canonical = (root / "docs/releases/MVP-RELEASE.md").resolve()
        if requested != canonical:
            raise SystemExit("Release packet requires canonical record docs/releases/MVP-RELEASE.md.")
    print(
        build_packet(
            root,
            args.phase,
            item=args.item,
            feature=args.feature,
            release=args.release,
            budget=args.budget_chars,
        ),
        end="",
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
