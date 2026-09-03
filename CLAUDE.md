# CLAUDE.md — biosciences-architecture

## Purpose

Repository Analyzer Framework and workspace architecture snapshots for the Open Biosciences platform. This repo is owned by the **Platform Architect** agent. It holds **no governance artifacts**: the Platform Architect authors platform ADRs in `biosciences-mcp`.

## What Lives Here

- `ra_agents/`, `ra_orchestrators/`, `ra_tools/` — Repository Analyzer Framework
- `workspace_architecture_20260301/` — dated workspace snapshot (repo catalog, ownership, dependency map, stack, migration status)
- `docs/` — empty

## Where the governance artifacts are

They moved twice: to `biosciences-program` on 2026-02-27, then to `biosciences-mcp` on 2026-03-03 (program `83d6c67`, mcp `5278c4e`). The placement rule that settles this is `biosciences-program/docs/adr/README.md` (2026-09-02): platform ADRs sit in the repo closest to their use.

| Artifact | Original Location | Current Location |
|----------|-------------------|------------------|
| Platform ADRs (001-006; 007 proposed) | `docs/adr/accepted/` | `biosciences-mcp/docs/adr/` |
| 13 MCP server specs | `specs/` | `biosciences-mcp/specs/` |
| .specify config | `.specify/` | `biosciences-mcp/.specify/` |
| 9 SpecKit commands | `.claude/commands/speckit.*.md` | `biosciences-mcp/.claude/commands/speckit.*.md` (legacy layout) |
| Platform engineering rationale | `docs/platform-engineering-rationale.md` | `biosciences-mcp/docs/platform-engineering-rationale.md` |
| SpecKit process docs | `docs/speckit-*.md` | `biosciences-mcp/docs/speckit-*.md` |
| ADR placement rule and index | — | `biosciences-program/docs/adr/README.md` |

**Rationale:** ADR-006 (Single Writer) mandates one canonical location per artifact. The location chosen is the one closest to where the ADRs are used, which is the MCP platform repo; program-scoped decisions would live in `biosciences-program` as `ADR-PRG-*`. The Platform Architect authors platform ADRs in `biosciences-mcp`.

## Governance Rules

1. **ADRs are normative** — all repos must comply with accepted platform ADRs (in `biosciences-mcp/docs/adr/accepted/`), except where a repo records a scoped deviation in its own `docs/adr/README.md`
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
