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

## Pre-Migration Location

Until Wave 1 migration completes, these documents live at:
`/home/donbr/graphiti-org/lifesciences-research/docs/adr/accepted/`
