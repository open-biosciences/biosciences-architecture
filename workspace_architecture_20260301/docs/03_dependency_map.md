# Cross-Repo Dependency Map — Open Biosciences

## Dependency Rules

1. `biosciences-program` and `biosciences-skills` have **no upstream dependencies** — they are pure providers
2. `biosciences-architecture` depends on biosciences-program (for ADRs/schemas)
3. `biosciences-mcp` depends on biosciences-program (ADR compliance)
4. `biosciences-deepagents` and `biosciences-temporal` consume biosciences-mcp tools
5. `biosciences-memory` is consumed by biosciences-research and biosciences-deepagents
6. `biosciences-evaluation` reads from all repos but no repo depends on it
7. `marketplace` copies from 4 source repos but introduces no runtime coupling

## Full Edge List

### Foundation → All

| From | To | Dependency Type | Evidence |
|------|----|----------------|----------|
| biosciences-program | all 12 repos | ADRs, specs, governance | All repos reference ADR-001 through ADR-006 |
| biosciences-skills | all consumer repos | Domain skills | Skills consumed via `.claude/skills/` |

### Foundation → Platform

| From | To | Dependency Type | Evidence |
|------|----|----------------|----------|
| biosciences-program | biosciences-mcp | ADR-001 (schema), ADR-004 (lifecycle) | Server implementations follow Fuzzy-to-Fact, Biolink schema |
| biosciences-program | biosciences-memory | ADR-001 (entity types) | Entity types align with Biolink schema |

### Platform → Orchestration

| From | To | Dependency Type | Evidence |
|------|----|----------------|----------|
| biosciences-mcp | biosciences-deepagents | MCP tools (HTTP gateway) | `apps/api/shared/mcp.py` connects to `https://biosciences-mcp.fastmcp.app/mcp` |
| biosciences-mcp | biosciences-temporal | MCP tools (Stdio transport) | `agents/base.py` spawns `src/biosciences_mcp/servers/gateway.py` |
| biosciences-mcp | biosciences-research | MCP tools (via graph-builder skill) | Competency questions invoke MCP search/get tools |
| biosciences-memory | biosciences-deepagents | Graph persistence | PERSIST phase writes via `persist_to_graphiti` tool |
| biosciences-memory | biosciences-research | Graph persistence | Research results stored with `group_id` namespaces |

### Marketplace (Distribution)

| From | To | Dependency Type | Evidence |
|------|----|----------------|----------|
| biosciences-mcp | marketplace | Tool definitions copied | 12 MCP server plugin directories |
| biosciences-skills | marketplace | Skills copied | `domain-skills/skills/` mirrors `.claude/skills/` |
| platform-skills | marketplace | Commands + skill copied | `platform-tools/` mirrors `.claude/commands/` + `.claude/skills/` |
| biosciences-program | marketplace | SpecKit commands copied | `speckit/commands/` mirrors `.claude/commands/speckit.*` |

### Validation (Observational)

| From | To | Dependency Type | Evidence |
|------|----|----------------|----------|
| all repos | biosciences-evaluation | Read-only measurement | Quality gates defined in evaluation rubrics |

## Integration Protocols

### Fuzzy-to-Fact (ADR-001 S3)
- **Enforced by:** all 12 MCP servers in biosciences-mcp
- **Consumed by:** deepagents (7 specialist phases), temporal (5 workflow phases), research (via graph-builder skill)
- **Flow:** Natural language query → `search_*` → ranked candidates with CURIEs → `get_*` with exact CURIE

### Token Budgeting
- **Enforced by:** all 12 MCP servers (`slim=true` parameter)
- **Consumed by:** all agent systems during exploration phase
- **Effect:** 5-10x reduction in response tokens (20 vs 115-300)

### Graphiti Namespaces
- **Priming:** `open-biosciences-migration-2026-priming` (read-only, never mutate)
- **Working:** `open-biosciences-migration-2026` (mutable, active decisions)
- **Per-CQ:** Each competency question gets its own `group_id` for graph isolation
