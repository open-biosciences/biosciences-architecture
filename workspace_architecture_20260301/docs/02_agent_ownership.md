# Agent Ownership Map — Open Biosciences

## 9-Agent Team

| # | Agent | Primary Repos | Role | Interfaces With |
|---|-------|---------------|------|-----------------|
| 1 | Program Director | biosciences-program | Cross-repo coordination, migration tracking, ADR governance | All agents (coordination hub) |
| 2 | Platform Architect | biosciences-architecture | Repository Analyzer Framework, ADR authoring, schema stewardship | All agents (architectural authority) |
| 3 | MCP Platform Engineer | biosciences-mcp | 12 FastMCP servers, gateway, 697+ tests | Agents 5, 6, 7 (tool consumers) |
| 4 | Memory Engineer | biosciences-memory | Graphiti/Neo4j knowledge graph layer, namespace policies | Agents 5, 6 (graph consumers) |
| 5 | Deep Agents Engineer | biosciences-deepagents | LangGraph supervisor + 7 specialists + React UI | Agents 3, 4 (tools + persistence) |
| 6 | Research Workflows Engineer | biosciences-research | Competency questions, RAG evaluation, graph-builder | Agents 3, 4 (tools + persistence) |
| 7 | Temporal Engineer | biosciences-temporal | PydanticAI + Temporal.io durable workflows | Agent 3 (MCP tools) |
| 8 | Quality & Skills Engineer | biosciences-evaluation, biosciences-skills, platform-skills, marketplace | Evaluation, skills library, test quality, marketplace | All agents (quality gates) |
| 9 | Education & Workspace Engineer | biosciences-education, biosciences-workspace-template | Training, tutorials, bootstrap scripts | All agents (onboarding) |

## Ownership Rules

1. Each repo has exactly one owning agent
2. Agent 8 owns the most repos (4) spanning quality, skills, and marketplace
3. Agent 9 owns the education + workspace pair (coordinated content + setup)
4. Agents 1 and 2 are "root providers" — their artifacts are consumed by all repos
5. Agents 5, 6, 7 are "consumers" — they consume MCP tools and memory services

## Agent Communication Patterns

```
Program Director (1) ←──── migration status ────→ All agents
Platform Architect (2) ←── ADR compliance ───────→ All agents
MCP Engineer (3) ←──────── tool invocations ─────→ Agents 5, 6, 7
Memory Engineer (4) ←───── graph persistence ────→ Agents 5, 6
Quality Engineer (8) ←──── quality gates ─────────→ All agents
```
