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
