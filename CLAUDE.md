# CLAUDE.md — biosciences-architecture

## Purpose

System architecture documents and governance specifications for the Open Biosciences platform. This repo is owned by the **Platform Architect** agent.

## What Lives Here

- `ra_agents/`, `ra_orchestrators/`, `ra_tools/` — Repository Analyzer Framework
- `docs/` — empty (ADRs and process docs migrated to `biosciences-program`)

## What Moved to `biosciences-program`

The following artifacts were migrated to `biosciences-program` as part of the governance consolidation (2026-02-27). The Program Director repo is now the single home for all governance artifacts:

| Artifact | Original Location | New Location |
|----------|-------------------|--------------|
| 6 ADRs (001-006) | `docs/adr/accepted/` | `biosciences-program/docs/adr/accepted/` |
| 13 MCP server specs | `specs/` | `biosciences-program/specs/` |
| .specify config | `.specify/` | `biosciences-program/.specify/` |
| 9 SpecKit commands | `.claude/commands/speckit.*.md` | `biosciences-program/.claude/commands/speckit.*.md` |
| Platform engineering rationale | `docs/platform-engineering-rationale.md` | `biosciences-program/docs/platform-engineering-rationale.md` |
| SpecKit process docs | `docs/speckit-*.md` | `biosciences-program/docs/speckit-*.md` |

**Rationale:** ADR-006 (Single Writer) mandates one canonical location per artifact. The Program Director owns cross-repo governance, making `biosciences-program` the natural home for ADRs, specs, and SpecKit tooling. The Platform Architect still authors ADRs but does so via the program repo.

## Governance Rules

1. **ADRs are normative** — all repos must comply with accepted ADRs (now in `biosciences-program/docs/adr/accepted/`)
2. **Schema changes require ADR updates** — no model/envelope changes without updating ADR-001
3. **New servers require architecture review** — adding an MCP server needs Platform Architect sign-off
4. **Version bumps** — ADR versions increment on any normative change (v1.0 → v1.1)
5. **Deprecation** — ADRs are deprecated, never deleted; superseded ADRs link to their replacement

## Key Specifications (reference — canonical source is biosciences-program)

### Fuzzy-to-Fact Protocol (ADR-001 §3)
- Phase 1: Fuzzy search → ranked candidates with CURIEs
- Phase 2: Strict lookup → requires resolved CURIE
- Failure mode: `UNRESOLVED_ENTITY` error with recovery hints

### Agentic Biolink Schema (ADR-001 §4)
- Flattened JSON (no deep TRAPI nesting)
- Every entity includes `cross_references` object
- 22-key cross-reference registry (§5)
- Null handling: omit keys entirely (never use `null` or empty string)

## Subsystem Context

The `ra_orchestrators/` subdirectory contains an independent orchestration framework with its own
444-line CLAUDE.md. Read `ra_orchestrators/CLAUDE.md` before working with that subsystem.
