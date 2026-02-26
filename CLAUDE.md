# CLAUDE.md — biosciences-architecture

## Purpose

System architecture documents, ADRs, and governance specifications for the Open Biosciences platform. This repo is owned by the **Platform Architect** agent.

## Key Documents

| Document | Status | Purpose |
|----------|--------|---------|
| ADR-001 v1.4 | Approved | Agentic-First Architecture — Hybrid Client, Fuzzy-to-Fact protocol, Agentic Biolink schema |
| ADR-002 v1.0 | Accepted | Project Skills as Platform Engineering (`.claude/skills/` pattern) |
| ADR-003 v1.0 | Accepted | SpecKit SDLC — specification-driven development workflow |
| ADR-004 v1.0 | Accepted | FastMCP Lifecycle Management (shutdown hook antipattern) |
| ADR-005 v1.0 | Accepted | Git Worktrees for Parallel Development |
| ADR-006 v1.0 | Accepted | Single Writer Package Architecture |
| Platform Engineering Rationale | Reference | Team topology and design rationale |

## Directory Structure (post-migration)

```
biosciences-architecture/
├── docs/
│   ├── adr/
│   │   ├── accepted/           # Approved ADRs (normative)
│   │   │   ├── adr-001-v1.4.md
│   │   │   ├── adr-002-v1.0.md
│   │   │   ├── adr-003-v1.0.md
│   │   │   ├── adr-004-v1.0.md
│   │   │   ├── adr-005-v1.0.md
│   │   │   └── adr-006-v1.0.md
│   │   └── proposed/           # Draft ADRs under review
│   └── platform-engineering-rationale.md
└── schemas/                    # Normative JSON schemas
```

## Governance Rules

1. **ADRs are normative** — all repos must comply with accepted ADRs
2. **Schema changes require ADR updates** — no model/envelope changes without updating ADR-001
3. **New servers require architecture review** — adding an MCP server needs Platform Architect sign-off
4. **Version bumps** — ADR versions increment on any normative change (v1.0 → v1.1)
5. **Deprecation** — ADRs are deprecated, never deleted; superseded ADRs link to their replacement

## Key Specifications

### Fuzzy-to-Fact Protocol (ADR-001 §3)
- Phase 1: Fuzzy search → ranked candidates with CURIEs
- Phase 2: Strict lookup → requires resolved CURIE
- Failure mode: `UNRESOLVED_ENTITY` error with recovery hints

### Agentic Biolink Schema (ADR-001 §4)
- Flattened JSON (no deep TRAPI nesting)
- Every entity includes `cross_references` object
- 22-key cross-reference registry (§5)
- Null handling: omit keys entirely (never use `null` or empty string)

### Normative Envelopes (ADR-001 §8)
- **Pagination Envelope**: All list tools must use `PaginationEnvelope`
- **Error Envelope**: All errors must use `ErrorEnvelope` with recovery hints
- **Error Code Registry**: 6 standard error codes (§9)

## Subsystem Context

The `ra_orchestrators/` subdirectory contains an independent orchestration framework with its own
444-line CLAUDE.md. Read `ra_orchestrators/CLAUDE.md` before working with that subsystem.

## SpecKit Commands (ADR-003)

The canonical SpecKit SDLC commands live in `.claude/commands/` in this repo:

| Command | File | Purpose |
|---------|------|---------|
| `/speckit.constitution` | `speckit.constitution.md` | Establish project principles (one-time) |
| `/speckit.specify` | `speckit.specify.md` | Create feature specification |
| `/speckit.clarify` | `speckit.clarify.md` | Surface underspecified areas |
| `/speckit.plan` | `speckit.plan.md` | Create implementation plan |
| `/speckit.tasks` | `speckit.tasks.md` | Generate actionable tasks |
| `/speckit.analyze` | `speckit.analyze.md` | Cross-artifact consistency check |
| `/speckit.implement` | `speckit.implement.md` | Execute bounded implementation |
| `/speckit.checklist` | `speckit.checklist.md` | Pre-flight checklist |
| `/speckit.taskstoissues` | `speckit.taskstoissues.md` | Convert tasks to GitHub issues |

SpecKit commands are governance artifacts — they define the SDLC process for the whole platform
and belong alongside the ADRs that mandate them (ADR-003). Domain execution skills remain in
`biosciences-skills/.claude/skills/`.

## Pre-Migration Location

Until Wave 1 migration completes, these documents live at:
`/home/donbr/graphiti-org/lifesciences-research/docs/adr/accepted/`

## SpecKit Specification Artifacts

Two directories from the `lifesciences-research` predecessor project have been migrated here as archival architectural artifacts. They are copied **as-is** — internal references to `src/lifesciences_mcp/` and original file paths are intentionally preserved to maintain the audit trail.

### `specs/` — MCP Server Specifications

| Property | Value |
|----------|-------|
| Source | `lifesciences-research/specs/` |
| Contents | 13 MCP server specification directories (`001-hgnc-mcp-server` through `013-clinicaltrials-mcp-server`) |
| Files | 143 files |
| Format | Each directory: spec.md, plan.md, tasks.md, data-model.md, research.md, quickstart.md, contracts/, checklists/, compliance analyses |
| Created by | `/scaffold-fastmcp-v2` + `/speckit.*` commands |
| ADR refs | ADR-001 (Agentic-First), ADR-003 (SpecKit SDLC), ADR-006 (Single Writer Package) |

These represent the complete design record for all 12 life sciences API integrations. Implementations live in `biosciences-mcp/src/biosciences_mcp/`.

> **Note:** Internal cross-references in spec files point to `src/lifesciences_mcp/` (original package name). The implementation has since been renamed to `biosciences_mcp` in `biosciences-mcp/`. References are not updated here to preserve specification integrity.

### `.specify/` — SpecKit Framework Configuration

| Property | Value |
|----------|-------|
| Source | `lifesciences-research/.specify/` |
| Contents | Constitution, templates, bash scripts |
| Files | 11 files |
| Subdirectories | `memory/` (constitution.md), `templates/` (5 markdown templates), `scripts/bash/` (5 automation scripts) |

The `.specify/` directory is the SpecKit process tooling used to generate the `specs/` artifacts. Key files:
- `memory/constitution.md` — 6 core principles, forbidden/required patterns, governance process
- `templates/spec-template.md`, `plan-template.md`, `tasks-template.md`, etc. — scaffolding templates
- `scripts/bash/create-new-feature.sh`, `update-agent-context.sh` — automation

> **Note:** Scripts reference `lifesciences-research`-era paths. They are preserved as-is for reference — update paths before running in the new workspace.

### SpecKit Process Documents (in `docs/`)

| File | Description | Original Path |
|------|-------------|---------------|
| `docs/speckit-standard-prompt-v2.md` | v2 (current) — ADR compliance table, 13 API canonical prompts, tier reference, anti-patterns | `lifesciences-research/docs/speckit-standard-prompt-v2.md` |
| `docs/speckit-standard-prompt.md` | v1 (legacy) — preserved for history/audit trail | `lifesciences-research/docs/speckit-standard-prompt.md` |
| `docs/speckit-scaffold-process-timeline-v2.md` | v2 — Mermaid workflow timeline, current vs optimized scaffolding process | `lifesciences-research/docs/speckit-scaffold-process-timeline-v2.md` |

These are **architectural governance documents** — they define how the SpecKit SDLC process maps to ADRs and how to produce specification artifacts. They are owned by the Platform Architect, not the Research Workflows Engineer, and live here alongside the ADRs they reference.

> **Migration note:** These docs were originally assigned to `biosciences-research` in the Wave 4 migration tracker. That assignment was incorrect — they are process/architecture documents, not research outputs. The migration tracker has been updated accordingly.
