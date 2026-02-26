#!/usr/bin/env python3
"""Workspace-level RA Orchestrator for cross-repo analysis.

Analyzes any repository in the open-biosciences workspace and produces:
- Per-repo architecture docs (components, diagrams, data flows, API reference)
- Workspace-level dependency map and topology diagram
- Migration status and wave readiness assessment
- Cross-repo synthesis narrative
- Ranked optimization recommendations
- Final README

Usage:
    python -m ra_orchestrators.workspace_orchestrator biosciences-mcp
    python -m ra_orchestrators.workspace_orchestrator biosciences-architecture
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions

from .base_orchestrator import BaseOrchestrator


class WorkspaceOrchestrator(BaseOrchestrator):
    """Orchestrator for workspace-level cross-repo analysis.

    Targets any repository in the open-biosciences workspace by resolving
    its absolute path from the workspace root. Injects absolute paths into
    all agent task prompts so agents use Read/Grep/Glob with explicit paths.

    Output is centralized in biosciences-architecture/ra_output/workspace/.
    No writes are made to the target repository.
    """

    # Known workspace repos for dependency mapping
    WORKSPACE_REPOS = [
        "biosciences-architecture",
        "biosciences-deepagents",
        "biosciences-education",
        "biosciences-evaluation",
        "biosciences-mcp",
        "biosciences-memory",
        "biosciences-program",
        "biosciences-research",
        "biosciences-skills",
        "biosciences-temporal",
        "biosciences-workspace-template",
    ]

    def __init__(
        self,
        target_repo: str = "biosciences-mcp",
        output_base_dir: Optional[Path] = None,
        show_tool_details: bool = True,
        use_timestamp: bool = True,
    ):
        """Initialize workspace orchestrator.

        Args:
            target_repo: Name of the workspace repo to analyze (e.g. 'biosciences-mcp')
            output_base_dir: Base directory for outputs (default: ra_output/ in this repo)
            show_tool_details: Whether to display detailed tool usage
            use_timestamp: Whether to append timestamp to output directory
        """
        # Resolve workspace root: .../biosciences-architecture/ra_orchestrators/ → .../open-biosciences/
        self._this_repo = Path(__file__).parent.parent.resolve()
        self.workspace_root = self._this_repo.parent.resolve()
        self.target_repo = target_repo
        self.target_repo_path = self.workspace_root / target_repo

        # Output goes under ra_output/workspace/{target_repo}_{timestamp}
        if output_base_dir is None:
            output_base_dir = self._this_repo / "ra_output"

        super().__init__(
            domain_name=f"workspace/{target_repo}",
            output_base_dir=output_base_dir,
            show_tool_details=show_tool_details,
            use_timestamp=use_timestamp,
        )

        # Sub-directory structure
        self.docs_dir = self.output_dir / "docs"
        self.diagrams_dir = self.output_dir / "diagrams"

        self.create_output_structure()

    def create_output_structure(self, subdirs: Optional[List[str]] = None):
        """Create docs/ and diagrams/ subdirectories, plus any extras in subdirs."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.diagrams_dir.mkdir(parents=True, exist_ok=True)
        if subdirs:
            for subdir in subdirs:
                (self.output_dir / subdir).mkdir(parents=True, exist_ok=True)

    def _load_agent_from_json(self, agent_name: str, domain: str = "architecture") -> AgentDefinition:
        """Load an AgentDefinition from its JSON file.

        Args:
            agent_name: Agent file stem (e.g. 'analyzer', 'dependency_mapper')
            domain: Subdirectory under ra_agents/ (default: 'architecture')

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
        """Load all 6 agents for the workspace analysis pipeline.

        Returns:
            Dict mapping agent names to AgentDefinition objects
        """
        return {
            "analyzer": self._load_agent_from_json("analyzer"),
            "doc_writer": self._load_agent_from_json("doc_writer"),
            "dependency_mapper": self._load_agent_from_json("dependency_mapper"),
            "migration_advisor": self._load_agent_from_json("migration_advisor"),
            "synthesis_writer": self._load_agent_from_json("synthesis_writer"),
            "optimization_advisor": self._load_agent_from_json("optimization_advisor"),
        }

    def get_allowed_tools(self) -> List[str]:
        """Get allowed tools for workspace analysis (read-only + write to output)."""
        return ["Read", "Write", "Grep", "Glob", "Bash"]

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
        """Inject workspace paths into a phase prompt template.

        Args:
            template: Prompt template with {repo_root}, {repo_name},
                      {workspace_root}, {output_dir} placeholders

        Returns:
            Formatted prompt string
        """
        return template.format(
            repo_root=self.target_repo_path,
            repo_name=self.target_repo,
            workspace_root=self.workspace_root,
            output_dir=self.output_dir,
            docs_dir=self.docs_dir,
            diagrams_dir=self.diagrams_dir,
        )

    # ─── Per-repo analysis phases (1–4) ────────────────────────────────────

    async def phase_1_component_inventory(self):
        """Phase 1: Component inventory for the target repo."""
        self.display_phase_header(1, "Component Inventory", "📋")

        await self.execute_phase(
            phase_name="Component Inventory",
            agent_name="analyzer",
            prompt=self._build_prompt(
                """Use the analyzer agent to create a comprehensive component inventory for {repo_name}.

Target repository: {repo_root}

Analyze the codebase at {repo_root} and document:
1. All Python modules and their purposes
2. Key classes and functions with descriptions
3. Public API surface vs internal implementation
4. Entry points and main interfaces
5. Configuration files (pyproject.toml, .env.example, etc.)

IMPORTANT: Use absolute paths when reading files. Read {repo_root}/pyproject.toml first to understand the project structure.

EXCLUDE these framework directories if analyzing biosciences-architecture itself:
- ra_orchestrators/ (analysis framework)
- ra_agents/ (analysis framework)
- ra_tools/ (analysis framework)
- ra_output/ (generated outputs)

Write your analysis to: {docs_dir}/01_component_inventory.md

Structure:
# Component Inventory — {repo_name}

## Project Overview
[Purpose from pyproject.toml / README]

## Public API
[List public modules, classes, functions with file:line references]

## Internal Implementation
[Internal modules and their roles]

## Entry Points
[Main entry points and CLI commands]

## Configuration
[Key config files and environment variables]

Include file paths and line numbers for all references."""
            ),
            client=self.client,
        )

    async def phase_2_architecture_diagrams(self):
        """Phase 2: Architecture diagrams for the target repo."""
        self.display_phase_header(2, "Architecture Diagrams", "🏗️")

        await self.execute_phase(
            phase_name="Architecture Diagrams",
            agent_name="analyzer",
            prompt=self._build_prompt(
                """Use the analyzer agent to create architecture diagrams for {repo_name}.

Target repository: {repo_root}
Component inventory: {docs_dir}/01_component_inventory.md

Generate Mermaid diagrams showing:
1. System architecture (layered view of {repo_name})
2. Component relationships and dependencies
3. Class hierarchies (if applicable)
4. Module dependency graph

Read {docs_dir}/01_component_inventory.md first to build on prior analysis.

Write your diagrams to: {diagrams_dir}/02_architecture_diagrams.md

Structure:
# Architecture Diagrams — {repo_name}

## System Architecture
```mermaid
[Layered architecture diagram]
```

## Component Relationships
```mermaid
[Component graph]
```

## Module Dependencies
```mermaid
[Module dependency diagram]
```

Include explanations for each diagram."""
            ),
            client=self.client,
        )

    async def phase_3_data_flows(self):
        """Phase 3: Data flow analysis for the target repo."""
        self.display_phase_header(3, "Data Flow Analysis", "🔄")

        await self.execute_phase(
            phase_name="Data Flow Analysis",
            agent_name="analyzer",
            prompt=self._build_prompt(
                """Use the analyzer agent to document data flows in {repo_name}.

Target repository: {repo_root}

Analyze and create sequence diagrams showing the primary data flows:
1. Main request/response flow through the system
2. Agent or workflow execution flow (if applicable)
3. External API call patterns (if applicable)
4. Error handling and recovery flows

Read source files in {repo_root} to understand actual implementation.

Write your analysis to: {docs_dir}/03_data_flows.md

Structure:
# Data Flow Analysis — {repo_name}

## Primary Flow
```mermaid
sequenceDiagram
[Main flow]
```
[Explanation]

## Secondary Flows
[Additional flows with diagrams and explanations]

Reference specific source files and line numbers."""
            ),
            client=self.client,
        )

    async def phase_4_api_reference(self):
        """Phase 4: API reference documentation."""
        self.display_phase_header(4, "API Reference", "📚")

        await self.execute_phase(
            phase_name="API Reference",
            agent_name="doc_writer",
            prompt=self._build_prompt(
                """Use the doc_writer agent to create API reference documentation for {repo_name}.

Target repository: {repo_root}

Document all public APIs, tools, and interfaces:
1. Function/method signatures with parameters and return types
2. MCP tool definitions (if this is biosciences-mcp)
3. Agent definitions and their capabilities
4. Configuration options and defaults
5. Usage examples

Read source files in {repo_root} to extract accurate documentation.

Write your documentation to: {docs_dir}/04_api_reference.md

Structure:
# API Reference — {repo_name}

## [Module/Component Name]
### function_name(params) → return_type
Description, parameters, returns, example usage.

Include working code examples and link to source files with line numbers."""
            ),
            client=self.client,
        )

    # ─── Workspace-level analysis phases (5–7) ─────────────────────────────

    async def phase_5_dependency_map(self):
        """Phase 5: Workspace dependency map."""
        self.display_phase_header(5, "Workspace Dependency Map", "🗺️")

        workspace_repos_str = "\n".join(f"- {workspace_root}/{repo}" for repo in self.WORKSPACE_REPOS
                                        for workspace_root in [str(self.workspace_root)])

        await self.execute_phase(
            phase_name="Workspace Dependency Map",
            agent_name="dependency_mapper",
            prompt=self._build_prompt(
                f"""Use the dependency_mapper agent to map workspace dependencies.

Target repository: {{repo_root}}
Workspace root: {{workspace_root}}

Known workspace repos (check which exist and read their CLAUDE.md / pyproject.toml):
{workspace_repos_str}

For each repo that exists, read:
1. CLAUDE.md — for declared dependencies and integration patterns
2. pyproject.toml — for Python package dependencies
3. README.md — for high-level description

Map the following known dependency edges (verify from files):
- biosciences-architecture ← all repos (ADRs and schemas)
- biosciences-skills ← all repos (skills library)
- biosciences-mcp ← biosciences-deepagents, biosciences-temporal, biosciences-research
- biosciences-memory ← biosciences-research, biosciences-deepagents
- biosciences-evaluation ← all repos (quality gates)

Focus especially on dependencies FROM/TO {{repo_name}}.

Write your analysis to: {{docs_dir}}/05_dependency_map.md

Structure:
# Workspace Dependency Map

## {{repo_name}} Dependencies
### Upstream (what {{repo_name}} depends on)
[List with evidence from files]

### Downstream (what depends on {{repo_name}})
[List with evidence from files]

## Full Workspace Edge List
[All confirmed dependency edges across workspace]

## Integration Points
[Specific API contracts, shared schemas, protocol definitions]

Reference file paths and line numbers for all claims."""
            ),
            client=self.client,
        )

    async def phase_6_workspace_topology(self):
        """Phase 6: Workspace topology diagram."""
        self.display_phase_header(6, "Workspace Topology Diagram", "🌐")

        await self.execute_phase(
            phase_name="Workspace Topology Diagram",
            agent_name="dependency_mapper",
            prompt=self._build_prompt(
                """Use the dependency_mapper agent to create the workspace topology diagram.

Read the dependency map: {docs_dir}/05_dependency_map.md

Create a comprehensive Mermaid diagram showing the full workspace dependency graph.
Highlight {repo_name} in the diagram to show its position in the workspace.

Write your diagram to: {diagrams_dir}/06_workspace_topology.md

Structure:
# Workspace Topology Diagram

## Full Workspace Dependency Graph
```mermaid
graph TD
    %% Foundation layer
    ARCH[biosciences-architecture]
    SKILLS[biosciences-skills]

    %% Platform layer
    MCP[biosciences-mcp]
    MEM[biosciences-memory]

    %% Orchestration layer
    DEEP[biosciences-deepagents]
    TEMP[biosciences-temporal]
    RES[biosciences-research]

    %% Validation layer
    EVAL[biosciences-evaluation]

    %% Edges (add all confirmed edges from dependency map)
    [dependency edges]

    %% Highlight target repo
    style {repo_name_clean}[repo node] fill:#f0f,stroke:#333
```

## Layer Analysis
[Describe each layer and the repos in it]

## {repo_name} Position
[Explain {repo_name}'s role and connections in the workspace]"""
            ),
            client=self.client,
        )

    async def phase_7_migration_status(self):
        """Phase 7: Migration status assessment."""
        self.display_phase_header(7, "Migration Status", "📊")

        migration_tracker = self.workspace_root / "biosciences-program" / "migration-tracker.md"

        await self.execute_phase(
            phase_name="Migration Status",
            agent_name="migration_advisor",
            prompt=self._build_prompt(
                f"""Use the migration_advisor agent to analyze migration status.

Migration tracker: {migration_tracker}
Target repository: {{repo_root}}
Workspace root: {{workspace_root}}

Read the migration tracker at {migration_tracker} (if it exists).
Also read {{workspace_root}}/biosciences-program/CLAUDE.md for program context.
Also read {{workspace_root}}/CLAUDE.md for workspace context.

Assess:
1. Current wave completion status (Wave 1-4)
2. {{repo_name}} migration status specifically
3. What has been migrated vs what remains
4. Blockers for next wave(s)
5. Wave 3 and Wave 4 readiness criteria

Write your analysis to: {{docs_dir}}/07_migration_status.md

Structure:
# Migration Status

## Wave Status Summary
| Wave | Repos | Status | Completion % |
|------|-------|--------|-------------|
[Wave status table]

## {{repo_name}} Migration Status
[Specific status of the target repo]

## Completed Migrations
[What has been successfully migrated]

## Active Work / In Progress
[Migrations underway]

## Blockers
[What is blocking next waves]

## Wave 3 Readiness Assessment
[Specific criteria and current state for Wave 3]

## Recommendations
[Next steps for migration progress]"""
            ),
            client=self.client,
        )

    # ─── Synthesis and recommendations (8–10) ──────────────────────────────

    async def phase_8_cross_repo_synthesis(self):
        """Phase 8: Cross-repo architecture synthesis."""
        self.display_phase_header(8, "Cross-Repo Synthesis", "🔗")

        await self.execute_phase(
            phase_name="Cross-Repo Synthesis",
            agent_name="synthesis_writer",
            prompt=self._build_prompt(
                """Use the synthesis_writer agent to write a cross-repo architecture synthesis.

Read all prior analysis outputs:
- {docs_dir}/01_component_inventory.md
- {diagrams_dir}/02_architecture_diagrams.md
- {docs_dir}/03_data_flows.md
- {docs_dir}/04_api_reference.md
- {docs_dir}/05_dependency_map.md
- {diagrams_dir}/06_workspace_topology.md
- {docs_dir}/07_migration_status.md

Write an integrated cross-repo narrative explaining:
1. How {repo_name} fits into the overall platform architecture
2. Integration patterns between {repo_name} and other repos
3. Shared conventions and where {repo_name} adheres to or diverges from them
4. The evolution path — where {repo_name} is heading based on migration status
5. Cross-cutting concerns: observability, error handling, authentication patterns

Write your synthesis to: {docs_dir}/08_cross_repo_synthesis.md

Structure:
# Cross-Repo Architecture Synthesis

## Platform Context
[How {repo_name} fits in the broader Open Biosciences platform]

## Integration Patterns
[Specific integration points with other repos, with evidence]

## Shared Conventions
[Where {repo_name} follows platform conventions]

## Divergences
[Where {repo_name} differs, and whether that is intentional]

## Evolution Path
[Where {repo_name} is heading based on migration status]

## Cross-Cutting Concerns
[Observability, error handling, auth, etc.]"""
            ),
            client=self.client,
        )

    async def phase_9_optimization_recommendations(self):
        """Phase 9: Ranked optimization recommendations."""
        self.display_phase_header(9, "Optimization Recommendations", "⚡")

        await self.execute_phase(
            phase_name="Optimization Recommendations",
            agent_name="optimization_advisor",
            prompt=self._build_prompt(
                """Use the optimization_advisor agent to produce ranked optimization recommendations.

Read all prior analysis outputs:
- {docs_dir}/01_component_inventory.md
- {docs_dir}/03_data_flows.md
- {docs_dir}/04_api_reference.md
- {docs_dir}/05_dependency_map.md
- {docs_dir}/07_migration_status.md
- {docs_dir}/08_cross_repo_synthesis.md

For {repo_name} specifically, identify:
1. Code quality and architecture optimization opportunities
2. Dependency consolidation or reduction opportunities
3. API or interface improvements
4. Migration acceleration opportunities
5. Developer experience improvements
6. Performance or reliability improvements

Rank each recommendation:
- Impact: High / Medium / Low
- Effort: Small (hours) / Medium (days) / Large (weeks)
- Priority = High Impact + Small/Medium Effort first

Write your recommendations to: {docs_dir}/09_optimization_recommendations.md

Structure:
# Optimization Recommendations — {repo_name}

## Executive Summary
[Top 3 recommendations with one-line rationale each]

## High Priority (High Impact, Low-Medium Effort)
### Recommendation Title
- **Impact**: High
- **Effort**: Small/Medium
- **Rationale**: [Why this matters]
- **Implementation**: [Specific steps]

## Medium Priority
[Medium impact or higher effort recommendations]

## Low Priority / Future
[Low impact or large effort items]

## Metrics
[How to measure success for top recommendations]"""
            ),
            client=self.client,
        )

    async def phase_10_final_readme(self):
        """Phase 10: Final README synthesis."""
        self.display_phase_header(10, "Final README", "📖")

        await self.execute_phase(
            phase_name="Final README",
            agent_name="optimization_advisor",
            prompt=self._build_prompt(
                """Use the optimization_advisor agent to write the final README for this analysis.

Read all analysis outputs:
- {docs_dir}/01_component_inventory.md
- {diagrams_dir}/02_architecture_diagrams.md
- {docs_dir}/03_data_flows.md
- {docs_dir}/04_api_reference.md
- {docs_dir}/05_dependency_map.md
- {diagrams_dir}/06_workspace_topology.md
- {docs_dir}/07_migration_status.md
- {docs_dir}/08_cross_repo_synthesis.md
- {docs_dir}/09_optimization_recommendations.md

Write a concise, executive-level README at: {output_dir}/README.md

Structure:
# Workspace Analysis: {repo_name}

> Analysis date: [today's date]
> Workspace: open-biosciences

## Key Findings
[3-5 bullet points — the most important insights from this analysis]

## {repo_name} at a Glance
[2-3 sentence description of what this repo does and its role in the platform]

## Architecture Summary
[Brief description with reference to 02_architecture_diagrams.md]

## Workspace Position
[How {repo_name} connects to other repos — reference 06_workspace_topology.md]

## Migration Status
[Current wave status — reference 07_migration_status.md]

## Top Recommendations
[Top 3 optimization recommendations — reference 09_optimization_recommendations.md]

## Document Index
| Document | Description |
|----------|-------------|
| [docs/01_component_inventory.md](docs/01_component_inventory.md) | Component inventory |
| [diagrams/02_architecture_diagrams.md](diagrams/02_architecture_diagrams.md) | Architecture diagrams |
| [docs/03_data_flows.md](docs/03_data_flows.md) | Data flow analysis |
| [docs/04_api_reference.md](docs/04_api_reference.md) | API reference |
| [docs/05_dependency_map.md](docs/05_dependency_map.md) | Workspace dependency map |
| [diagrams/06_workspace_topology.md](diagrams/06_workspace_topology.md) | Workspace topology diagram |
| [docs/07_migration_status.md](docs/07_migration_status.md) | Migration status |
| [docs/08_cross_repo_synthesis.md](docs/08_cross_repo_synthesis.md) | Cross-repo synthesis |
| [docs/09_optimization_recommendations.md](docs/09_optimization_recommendations.md) | Optimization recommendations |"""
            ),
            client=self.client,
        )

    # ─── Orchestration ──────────────────────────────────────────────────────

    async def run(self):
        """Run the 10-phase workspace analysis pipeline."""
        print(f"\n🎯 Target repository: {self.target_repo}")
        print(f"📁 Repo path: {self.target_repo_path}")
        print(f"🌐 Workspace root: {self.workspace_root}")

        if not self.target_repo_path.exists():
            raise ValueError(
                f"Target repository not found: {self.target_repo_path}\n"
                f"Available repos: {[r for r in self.WORKSPACE_REPOS if (self.workspace_root / r).exists()]}"
            )

        # Per-repo analysis (phases 1–4)
        await self.phase_1_component_inventory()
        await self.phase_2_architecture_diagrams()
        await self.phase_3_data_flows()
        await self.phase_4_api_reference()

        # Workspace-level analysis (phases 5–7)
        await self.phase_5_dependency_map()
        await self.phase_6_workspace_topology()
        await self.phase_7_migration_status()

        # Synthesis and recommendations (phases 8–10)
        await self.phase_8_cross_repo_synthesis()
        await self.phase_9_optimization_recommendations()
        await self.phase_10_final_readme()

        # Verify all expected outputs exist
        expected_files = [
            self.docs_dir / "01_component_inventory.md",
            self.diagrams_dir / "02_architecture_diagrams.md",
            self.docs_dir / "03_data_flows.md",
            self.docs_dir / "04_api_reference.md",
            self.docs_dir / "05_dependency_map.md",
            self.diagrams_dir / "06_workspace_topology.md",
            self.docs_dir / "07_migration_status.md",
            self.docs_dir / "08_cross_repo_synthesis.md",
            self.docs_dir / "09_optimization_recommendations.md",
            self.output_dir / "README.md",
        ]

        await self.verify_outputs(expected_files)


if __name__ == "__main__":
    import sys

    target_repo = sys.argv[1] if len(sys.argv) > 1 else "biosciences-mcp"
    orchestrator = WorkspaceOrchestrator(target_repo=target_repo)
    asyncio.run(orchestrator.run_with_client())
