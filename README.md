# biosciences-architecture

System architecture documents, ADRs, and governance specifications for the [Open Biosciences](https://github.com/open-biosciences) platform.

Owned by the **Platform Architect** agent. This is a root provider repository -- all other repos in the platform read architecture decisions and schemas from here.

## Contents

### Architecture Decision Records

Six accepted ADRs in `docs/adr/accepted/`:

| ADR | Title | Key Concepts |
|-----|-------|--------------|
| ADR-001 v1.4 | Agentic-First Architecture | Fuzzy-to-Fact protocol, Agentic Biolink schema, MCP tool design |
| ADR-002 v1.0 | Project Skills as Platform Engineering | Skills library structure, domain skill conventions |
| ADR-003 v1.0 | SpecKit Specification-Driven Development | SDLC workflow commands, specification-first process |
| ADR-004 v1.0 | FastMCP Lifecycle Management | MCP server patterns, lifecycle hooks |
| ADR-005 v1.0 | Git Worktrees for Parallel Development | Worktree conventions, branch management |
| ADR-006 v1.0 | Single Writer Package Architecture | One-repo-per-package ownership model |

### Platform Engineering Rationale

`docs/platform-engineering-rationale.md` -- team topology, design rationale, and the 9-agent model that governs the platform.

## SpecKit Artifacts (Migrated from `lifesciences-research`)

The following directories were migrated from the `lifesciences-research` predecessor repository as archival architectural artifacts. Files are copied **as-is** — internal cross-references to `lifesciences_mcp` package paths are intentionally preserved.

### Directories

| Directory | Description |
|-----------|-------------|
| `specs/` | 13 MCP server specification directories (`001-hgnc-mcp-server` through `013-clinicaltrials-mcp-server`) — the complete design record for all life sciences API integrations, produced by the SpecKit SDLC process. 143 files total. |
| `.specify/` | SpecKit framework configuration — project constitution (`memory/constitution.md`), 5 markdown templates, and 5 bash automation scripts. 11 files total. |

### SpecKit Process Documents (`docs/`)

| File | Description |
|------|-------------|
| `docs/speckit-standard-prompt-v2.md` | v2 (current) — ADR compliance table, 13 API canonical prompts, tier reference, anti-patterns |
| `docs/speckit-standard-prompt.md` | v1 (legacy) — preserved for history/audit trail |
| `docs/speckit-scaffold-process-timeline-v2.md` | v2 — Mermaid workflow timeline, current vs optimized scaffolding process |

**Provenance:** All files were created in `lifesciences-research` (predecessor repo at `/home/donbr/graphiti-org/lifesciences-research/`) and migrated here as archival artifacts. These are governance and specification artifacts owned by the Platform Architect; they live here alongside the ADRs they reference (ADR-001, ADR-003, ADR-006).

## Usage

This repo contains documentation only (no runnable code). Reference these ADRs when:

- Designing new MCP servers (ADR-001, ADR-004)
- Creating or modifying domain skills (ADR-002)
- Following the SpecKit SDLC workflow (ADR-003)
- Structuring packages across repos (ADR-006)

## Dependencies

None. This is a foundational repo with no upstream dependencies.

**Downstream consumers:** All 10 other repos in the Open Biosciences platform read ADRs and schemas from this repository.

## Related Repos

- [biosciences-skills](https://github.com/open-biosciences/biosciences-skills) -- implements ADR-002 and ADR-003
- [biosciences-mcp](https://github.com/open-biosciences/biosciences-mcp) -- implements ADR-001 and ADR-004
- [biosciences-program](https://github.com/open-biosciences/biosciences-program) -- migration coordination

## License

MIT
