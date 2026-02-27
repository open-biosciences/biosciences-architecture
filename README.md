# biosciences-architecture

System architecture documents and governance specifications for the [Open Biosciences](https://github.com/open-biosciences) platform.

Owned by the **Platform Architect** agent (Agent 2). This is the root provider repository — no upstream dependencies.

## Migration Status

| Wave | Status | Completed |
|------|--------|-----------|
| Wave 1 — Foundation | ✅ Complete | 2026-02-25 (AGE-149) |
| Wave 1-ext — SpecKit artifacts | ✅ Complete | 2026-02-26 (AGE-183) |
| Governance consolidation | ✅ Complete | 2026-02-27 (AGE-184) |

## Current Contents

### Repository Analyzer Framework

- `ra_agents/` — Analysis agents
- `ra_orchestrators/` — Orchestration framework (has its own CLAUDE.md)
- `ra_tools/` — Analysis tools

### Governance Artifacts (migrated)

All governance artifacts have been consolidated into [`biosciences-program`](https://github.com/open-biosciences/biosciences-program) as the single canonical location per ADR-006 (Single Writer):

| Artifact | New Location |
|----------|-------------|
| 6 ADRs (001-006) | `biosciences-program/docs/adr/accepted/` |
| 13 MCP server specs (143 files) | `biosciences-program/specs/` |
| .specify config (11 files) | `biosciences-program/.specify/` |
| 9 SpecKit commands | `biosciences-program/.claude/commands/` |
| Platform engineering rationale | `biosciences-program/docs/` |
| SpecKit process docs | `biosciences-program/docs/` |

**Rationale:** The Program Director owns cross-repo governance and coordination. Centralizing ADRs, specs, and SpecKit tooling in the program repo gives a single source of truth for the SDLC process, while the Platform Architect continues to author ADRs via that repo.

## Usage

Reference ADRs (now in `biosciences-program`) when:

- Designing new MCP servers (ADR-001, ADR-004)
- Creating or modifying domain skills (ADR-002)
- Following the SpecKit SDLC workflow (ADR-003)
- Structuring packages across repos (ADR-006)

## Dependencies

None. This is the foundational root provider repo with no upstream dependencies.

**Downstream consumers:** All 11 other repos in the Open Biosciences platform read ADRs from `biosciences-program`.

## Related Repos

- [biosciences-program](https://github.com/open-biosciences/biosciences-program) — governance artifacts, migration coordination
- [biosciences-skills](https://github.com/open-biosciences/biosciences-skills) — implements ADR-002 and ADR-003
- [biosciences-mcp](https://github.com/open-biosciences/biosciences-mcp) — implements ADR-001 and ADR-004

## License

MIT
