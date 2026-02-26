#!/usr/bin/env python3
"""Review Orchestrator — 4-agent review team for workspace analysis output.

Deploys a review team against a completed WorkspaceOrchestrator output to
produce a quality report and prioritized action backlog.

Review team:
  accuracy_auditor      — cross-checks every factual claim against source
  gap_analyst           — identifies what is present in source but absent from docs
  adr_compliance_checker — validates ADR-001–006 MUST/SHALL compliance
  strategy_advisor      — synthesizes findings into a P0–P3 action backlog

Output structure (written into the prior run's review/ subdirectory):
  review/
    README.md               (Phase 5: overall verdict + index)
    01_accuracy_audit.md    (Phase 1: VERIFIED / INACCURATE / UNVERIFIABLE table)
    02_gap_analysis.md      (Phase 2: gap register with severity)
    03_adr_compliance.md    (Phase 3: compliance matrix by ADR)
    04_strategy_backlog.md  (Phase 4: P0–P3 prioritized action items)

Usage:
    # Explicit path:
    python -m ra_orchestrators.review_orchestrator \\
        ra_output/workspace/biosciences-mcp_20260225_191152

    # Auto-discover latest run for a repo:
    python -m ra_orchestrators.review_orchestrator --repo biosciences-mcp

    # Auto-discover most recent run across all repos:
    python -m ra_orchestrators.review_orchestrator --latest
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions

from .base_orchestrator import BaseOrchestrator


class ReviewOrchestrator(BaseOrchestrator):
    """Orchestrator for reviewing workspace analysis output.

    Targets the output directory of a prior WorkspaceOrchestrator run and
    produces a quality report + prioritized action backlog in a review/
    subdirectory alongside the generated docs.

    No writes are made to source repositories or to the prior analysis files.
    Only review/ is created or overwritten.
    """

    def __init__(self, prior_run_dir: Path):
        """Initialize the review orchestrator.

        Args:
            prior_run_dir: Path to a completed WorkspaceOrchestrator output
                           directory (e.g. ra_output/workspace/biosciences-mcp_20260225_191152)

        Raises:
            ValueError: If prior_run_dir does not exist or lacks a docs/ subdirectory
        """
        prior_run_dir = Path(prior_run_dir).resolve()

        if not prior_run_dir.exists():
            raise ValueError(
                f"Prior run directory not found: {prior_run_dir}\n"
                f"Pass an existing workspace analysis directory."
            )

        if not (prior_run_dir / "docs").exists():
            raise ValueError(
                f"Not a valid workspace analysis directory: {prior_run_dir}\n"
                f"Expected docs/ subdirectory. Run WorkspaceOrchestrator first."
            )

        # Extract target repo name from directory name: "biosciences-mcp_20260225_191152" → "biosciences-mcp"
        dir_name = prior_run_dir.name
        # rsplit on "_", maxsplit=2 splits "biosciences-mcp_20260225_191152" into
        # ["biosciences-mcp", "20260225", "191152"] — take [0]
        parts = dir_name.rsplit("_", 2)
        self.target_repo = parts[0] if len(parts) >= 3 else dir_name

        # Resolve workspace root from this file's location:
        # .../biosciences-architecture/ra_orchestrators/ → .../open-biosciences/
        self._this_repo = Path(__file__).parent.parent.resolve()
        self.workspace_root = self._this_repo.parent.resolve()

        self.target_repo_path = self.workspace_root / self.target_repo
        self.arch_repo_path = self.workspace_root / "biosciences-architecture"
        self.adrs_dir = self.arch_repo_path / "docs" / "adr" / "accepted"

        # Paths within the prior run
        self.prior_run_dir = prior_run_dir
        self.docs_dir = prior_run_dir / "docs"
        self.diagrams_dir = prior_run_dir / "diagrams"

        # Initialize base orchestrator with no timestamp; we control the output dir manually
        super().__init__(
            domain_name="review",
            output_base_dir=prior_run_dir,
            use_timestamp=False,
        )

        # Override BaseOrchestrator's computed output_dir.
        # BaseOrchestrator would create prior_run_dir / "review_analysis";
        # we want prior_run_dir / "review".
        self.output_dir = prior_run_dir / "review"
        self.review_dir = self.output_dir

        self.create_output_structure()

    def create_output_structure(self, subdirs: Optional[List[str]] = None):
        """Create the review/ subdirectory."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if subdirs:
            for subdir in subdirs:
                (self.output_dir / subdir).mkdir(parents=True, exist_ok=True)

    def _load_agent_from_json(self, agent_name: str, domain: str = "review") -> AgentDefinition:
        """Load an AgentDefinition from its JSON file.

        Args:
            agent_name: Agent file stem (e.g. 'accuracy_auditor')
            domain: Subdirectory under ra_agents/ (default: 'review')

        Returns:
            AgentDefinition loaded from JSON
        """
        agent_file = self._this_repo / "ra_agents" / domain / f"{agent_name}.json"
        with open(agent_file) as f:
            data = json.load(f)

        return AgentDefinition(
            description=data["description"],
            prompt=data["prompt"],
            tools=data.get("tools", ["Read", "Grep", "Glob", "Write"]),
            model=data.get("model", "sonnet"),
        )

    def get_agent_definitions(self) -> Dict[str, AgentDefinition]:
        """Load all 4 review agents."""
        return {
            "accuracy_auditor": self._load_agent_from_json("accuracy_auditor"),
            "gap_analyst": self._load_agent_from_json("gap_analyst"),
            "adr_compliance_checker": self._load_agent_from_json("adr_compliance_checker"),
            "strategy_advisor": self._load_agent_from_json("strategy_advisor"),
        }

    def get_allowed_tools(self) -> List[str]:
        """Review agents read source + prior docs and write to review/."""
        return ["Read", "Write", "Grep", "Glob"]

    def create_client_options(
        self,
        permission_mode: str = "acceptEdits",
        cwd: str = ".",
    ) -> ClaudeAgentOptions:
        """Override to set cwd=workspace_root for cross-repo file access."""
        return super().create_client_options(
            permission_mode=permission_mode,
            cwd=str(self.workspace_root),
        )

    def _build_prompt(self, template: str) -> str:
        """Inject review paths into a phase prompt template.

        Placeholders:
            {prior_run_dir}   — absolute path to workspace analysis being reviewed
            {docs_dir}        — {prior_run_dir}/docs
            {diagrams_dir}    — {prior_run_dir}/diagrams
            {review_dir}      — {prior_run_dir}/review
            {target_repo_path} — absolute source path of the target repo
            {target_repo}     — repo name string
            {adrs_dir}        — accepted ADRs directory
        """
        return template.format(
            prior_run_dir=self.prior_run_dir,
            docs_dir=self.docs_dir,
            diagrams_dir=self.diagrams_dir,
            review_dir=self.review_dir,
            target_repo_path=self.target_repo_path,
            target_repo=self.target_repo,
            adrs_dir=self.adrs_dir,
        )

    # ─── Review phases ──────────────────────────────────────────────────────

    async def phase_1_accuracy_audit(self):
        """Phase 1: Cross-check documentation claims against source code."""
        self.display_phase_header(1, "Accuracy Audit", "🔍")

        await self.execute_phase(
            phase_name="Accuracy Audit",
            agent_name="accuracy_auditor",
            prompt=self._build_prompt(
                """You are the accuracy_auditor. Cross-check the documentation in {docs_dir} and {diagrams_dir} against the actual source code in {target_repo_path}.

Prior analysis directory: {prior_run_dir}
Source code: {target_repo_path}
Documentation to audit:
  - {docs_dir}/01_component_inventory.md
  - {diagrams_dir}/02_architecture_diagrams.md
  - {docs_dir}/03_data_flows.md
  - {docs_dir}/04_api_reference.md
  - {docs_dir}/05_dependency_map.md
  - {docs_dir}/07_migration_status.md
  - {docs_dir}/08_cross_repo_synthesis.md

For each factual claim (function names, class names, line references, behavior descriptions, API signatures):
1. Read the referenced source file and verify the claim
2. Classify each claim as VERIFIED, INACCURATE, or UNVERIFIABLE
3. For INACCURATE: provide the correction with source file:line
4. For UNVERIFIABLE: explain why the claim cannot be checked

Focus on high-impact claims: public API signatures, module paths, class hierarchies, tool names, and configuration.
Do not audit stylistic choices or opinions.

Write your audit to: {review_dir}/01_accuracy_audit.md

Structure:
# Accuracy Audit — {target_repo}

## Summary
[X claims verified, Y inaccurate, Z unverifiable]

## Findings Table
| Claim | Source Document | Status | Notes / Correction |
|-------|----------------|--------|-------------------|
[One row per verified/inaccurate/unverifiable claim — be specific]

## INACCURATE Claims (Detail)
[For each INACCURATE claim, provide full correction with source evidence]

## UNVERIFIABLE Claims
[List with reason for each]"""
            ),
            client=self.client,
        )

    async def phase_2_gap_analysis(self):
        """Phase 2: Identify what is in source but absent from documentation."""
        self.display_phase_header(2, "Gap Analysis", "🕳️")

        await self.execute_phase(
            phase_name="Gap Analysis",
            agent_name="gap_analyst",
            prompt=self._build_prompt(
                """You are the gap_analyst. Identify what is present in the source code at {target_repo_path} but absent or inadequately covered in the documentation at {docs_dir}.

Source code: {target_repo_path}
Documentation to check against:
  - {docs_dir}/01_component_inventory.md
  - {docs_dir}/03_data_flows.md
  - {docs_dir}/04_api_reference.md

Do NOT praise what is present. Only output gaps.

Focus areas:
1. Public functions/methods documented in docs/ that are missing from source (or vice versa)
2. Configuration options not mentioned in docs
3. Error handling paths not documented
4. Integration patterns present in source but absent from dependency map
5. CLI commands or entry points not documented

For each gap:
- Name the specific entity (function, class, config key, behavior)
- Provide source file:line where it lives
- Assign severity: CRITICAL / HIGH / MEDIUM / LOW
- Recommend specific resolution

Write your analysis to: {review_dir}/02_gap_analysis.md

Structure:
# Gap Analysis — {target_repo}

## Summary
[X CRITICAL, Y HIGH, Z MEDIUM, W LOW gaps found]

## Gap Register
| Gap | Source Location | Severity | Recommended Resolution |
|-----|----------------|----------|----------------------|
[One row per gap — be specific, no vague entries]

## CRITICAL Gaps (Detail)
[For each CRITICAL gap: what it is, why it matters, exact resolution]

## HIGH Gaps (Detail)
[Same format]"""
            ),
            client=self.client,
        )

    async def phase_3_adr_compliance(self):
        """Phase 3: Validate ADR-001–006 MUST/SHALL compliance."""
        self.display_phase_header(3, "ADR Compliance Check", "⚖️")

        await self.execute_phase(
            phase_name="ADR Compliance",
            agent_name="adr_compliance_checker",
            prompt=self._build_prompt(
                """You are the adr_compliance_checker. Validate the source code at {target_repo_path} against the normative requirements in ADR-001 through ADR-006.

ADR files: {adrs_dir}
Source code: {target_repo_path}

Read each ADR and extract every MUST/SHALL requirement. Then verify the source code complies.

ADRs to check:
  - {adrs_dir}/adr-001-v1.4.md  (Agentic-First Architecture, Fuzzy-to-Fact, Biolink schema)
  - {adrs_dir}/adr-002-v1.0.md  (Project Skills as Platform Engineering)
  - {adrs_dir}/adr-003-v1.0.md  (SpecKit SDLC)
  - {adrs_dir}/adr-004-v1.0.md  (FastMCP Lifecycle Management)
  - {adrs_dir}/adr-005-v1.0.md  (Git Worktrees for Parallel Development)
  - {adrs_dir}/adr-006-v1.0.md  (Single Writer Package Architecture)

For each MUST/SHALL:
- COMPLIANT: provide file:line evidence
- VIOLATION: provide file:line evidence and describe the violation
- NOT_APPLICABLE: explain why this ADR does not apply to {target_repo}
- UNVERIFIABLE: explain why compliance cannot be determined

Do not soften violations.

Write your compliance report to: {review_dir}/03_adr_compliance.md

Structure:
# ADR Compliance Report — {target_repo}

## Summary
[X COMPLIANT, Y VIOLATIONS, Z NOT_APPLICABLE, W UNVERIFIABLE]

## Compliance Matrix
| ADR | Requirement | Status | Evidence |
|-----|------------|--------|---------|
[One row per MUST/SHALL requirement]

## Violations (Detail)
[For each VIOLATION: exact requirement text, source file:line of violation, required remediation]

## NOT_APPLICABLE Rationale
[Brief explanation for each NOT_APPLICABLE entry]"""
            ),
            client=self.client,
        )

    async def phase_4_strategy_backlog(self):
        """Phase 4: Synthesize findings into P0–P3 action backlog."""
        self.display_phase_header(4, "Strategy Backlog", "📋")

        await self.execute_phase(
            phase_name="Strategy Backlog",
            agent_name="strategy_advisor",
            prompt=self._build_prompt(
                """You are the strategy_advisor. Synthesize findings from the three review documents into a prioritized action backlog.

Review findings to synthesize:
  - {review_dir}/01_accuracy_audit.md
  - {review_dir}/02_gap_analysis.md
  - {review_dir}/03_adr_compliance.md

IMPORTANT: Do not add new findings. Every action item MUST trace to a specific finding in one of the three input documents.

Priority levels:
- P0: Blocking — ADR violations, inaccuracies that would mislead users trying to use the API
- P1: High — CRITICAL gaps, significant inaccuracies in public API docs
- P2: Medium — HIGH gaps, moderate inaccuracies, non-critical ADR compliance issues
- P3: Low — MEDIUM/LOW gaps, style issues, minor improvements

For each action item:
1. Title: [P0] Fix X in Y  (Linear-compatible format)
2. Traces to: (exact finding from source document)
3. Remediation: specific steps to resolve
4. Effort: Small (hours) / Medium (days) / Large (weeks)

Write your backlog to: {review_dir}/04_strategy_backlog.md

Structure:
# Strategy Backlog — {target_repo}

## Executive Summary
[Overall health assessment: APPROVED / APPROVED_WITH_FINDINGS / NEEDS_REWORK]
[1-2 sentences on the most critical issues]

## P0 — Blocking
[Each item with title, traces-to, remediation, effort]

## P1 — High Priority
[Same format]

## P2 — Medium Priority
[Same format]

## P3 — Low Priority / Future
[Same format]

## Metrics
| Priority | Count |
|----------|-------|
| P0 | X |
| P1 | Y |
| P2 | Z |
| P3 | W |
| Total | N |"""
            ),
            client=self.client,
        )

    async def phase_5_review_readme(self):
        """Phase 5: Write overall review README with verdict and index."""
        self.display_phase_header(5, "Review README", "📖")

        await self.execute_phase(
            phase_name="Review README",
            agent_name="strategy_advisor",
            prompt=self._build_prompt(
                """You are the strategy_advisor. Write the overall review README for this analysis.

Read all four review documents:
  - {review_dir}/01_accuracy_audit.md
  - {review_dir}/02_gap_analysis.md
  - {review_dir}/03_adr_compliance.md
  - {review_dir}/04_strategy_backlog.md

Write a concise review summary to: {review_dir}/README.md

Structure:
# Review Report — {target_repo}

> Review date: 2026-02-25
> Prior analysis: {prior_run_dir}

## Overall Verdict
**[APPROVED / APPROVED_WITH_FINDINGS / NEEDS_REWORK]**

[1-3 sentences explaining the verdict]

## Key Findings
[3-5 bullet points — the most critical findings from all three audits]

## Action Required
[Summarize P0 and P1 items from the strategy backlog — these require attention before the next release]

## Document Index
| Document | Description | Key Metrics |
|----------|-------------|-------------|
| [01_accuracy_audit.md](01_accuracy_audit.md) | Factual accuracy of generated docs | X verified, Y inaccurate |
| [02_gap_analysis.md](02_gap_analysis.md) | Coverage gaps vs. source | X CRITICAL, Y HIGH gaps |
| [03_adr_compliance.md](03_adr_compliance.md) | ADR-001–006 compliance | X compliant, Y violations |
| [04_strategy_backlog.md](04_strategy_backlog.md) | Prioritized action items | X P0, Y P1, Z P2 |"""
            ),
            client=self.client,
        )

    # ─── Orchestration ──────────────────────────────────────────────────────

    async def run(self):
        """Run the 5-phase review pipeline."""
        print(f"\n🎯 Reviewing: {self.target_repo}")
        print(f"📁 Prior run: {self.prior_run_dir}")
        print(f"📝 Review output: {self.review_dir}")
        print(f"🌐 Workspace root: {self.workspace_root}")

        # Independent audit phases (1–3)
        await self.phase_1_accuracy_audit()
        await self.phase_2_gap_analysis()
        await self.phase_3_adr_compliance()

        # Synthesis phases (4–5) — depend on phases 1–3
        await self.phase_4_strategy_backlog()
        await self.phase_5_review_readme()

        # Verify all review outputs
        expected_files = [
            self.review_dir / "01_accuracy_audit.md",
            self.review_dir / "02_gap_analysis.md",
            self.review_dir / "03_adr_compliance.md",
            self.review_dir / "04_strategy_backlog.md",
            self.review_dir / "README.md",
        ]

        await self.verify_outputs(expected_files)


def _find_latest_run(workspace_output_dir: Path, repo: Optional[str] = None) -> Path:
    """Find the most recent workspace analysis run.

    Args:
        workspace_output_dir: ra_output/workspace/ directory
        repo: If given, find the latest run for this specific repo

    Returns:
        Path to the most recent run directory

    Raises:
        ValueError: If no matching runs are found
    """
    if not workspace_output_dir.exists():
        raise ValueError(f"Workspace output directory not found: {workspace_output_dir}")

    candidates = [
        d for d in workspace_output_dir.iterdir()
        if d.is_dir() and (d / "docs").exists()
    ]

    if repo:
        candidates = [d for d in candidates if d.name.startswith(f"{repo}_")]

    if not candidates:
        msg = f"No completed workspace analysis runs found"
        if repo:
            msg += f" for repo '{repo}'"
        msg += f" in {workspace_output_dir}"
        raise ValueError(msg)

    # Sort by directory name (timestamp is embedded: repo_YYYYMMDD_HHMMSS)
    candidates.sort(key=lambda d: d.name)
    return candidates[-1]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Review a completed workspace analysis with a 4-agent review team"
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--repo",
        metavar="REPO_NAME",
        help="Auto-discover latest run for this repo (e.g. biosciences-mcp)",
    )
    group.add_argument(
        "--latest",
        action="store_true",
        help="Auto-discover the most recent run across all repos",
    )
    parser.add_argument(
        "prior_run_dir",
        nargs="?",
        help="Explicit path to a workspace analysis directory",
    )

    args = parser.parse_args()

    # Resolve the prior run directory
    this_repo = Path(__file__).parent.parent.resolve()
    workspace_output_dir = this_repo / "ra_output" / "workspace"

    if args.prior_run_dir:
        prior_run = Path(args.prior_run_dir)
        # Allow relative paths from this repo
        if not prior_run.is_absolute():
            prior_run = this_repo / prior_run
    elif args.repo:
        prior_run = _find_latest_run(workspace_output_dir, repo=args.repo)
        print(f"Auto-discovered latest run for '{args.repo}': {prior_run.name}")
    elif args.latest:
        prior_run = _find_latest_run(workspace_output_dir)
        print(f"Auto-discovered most recent run: {prior_run.name}")
    else:
        # Default: latest run
        try:
            prior_run = _find_latest_run(workspace_output_dir)
            print(f"Auto-discovered most recent run: {prior_run.name}")
        except ValueError as e:
            parser.error(str(e))

    orchestrator = ReviewOrchestrator(prior_run_dir=prior_run)
    asyncio.run(orchestrator.run_with_client())
