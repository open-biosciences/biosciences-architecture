# Repository Catalog — Open Biosciences

## Summary

13 repositories under the `open-biosciences` GitHub organization. All MIT-licensed. Python >=3.11.

## Foundation Layer

| Repo | Agent | Purpose | Package | LOC | Status |
|------|-------|---------|---------|-----|--------|
| biosciences-program | #1 Program Director | Cross-repo coordination, ADRs, SpecKit SDLC, migration tracking | n/a (docs only) | 0 py / 68K md | Complete |
| biosciences-skills | #8 Quality & Skills | 9 domain skills (genomics, proteomics, pharmacology, clinical, CRISPR, graph-builder, reporting, quality-review, publication-pipeline) | n/a (skills only) | 0 py / 3.4K lines SKILL.md | Complete |
| biosciences-architecture | #2 Platform Architect | Repository Analyzer Framework (4 orchestrators, 14 agents, 3 tool integrations) | biosciences-architecture 0.1.0 | ~6,600 py | Complete |

### biosciences-program

Coordination-only repo. Contains:
- `docs/adr/accepted/` — 6 ADRs (001-006), normative for all repos
- `specs/` — 13 MCP server specifications (143 files)
- `.specify/` — SpecKit framework config (constitution, templates, scripts)
- `.claude/commands/` — 9 SpecKit slash commands
- `AGENTS.md` — 9-agent team definitions
- `migration-tracker.md` — 4-wave migration status

### biosciences-skills

Skill library consumed by all repos. Contains:
- 9 domain skills in `.claude/skills/biosciences-*/SKILL.md`
- Each skill: 250-670 lines, includes triggers, API patterns, MCP tool names, curl fallbacks
- Enforces Fuzzy-to-Fact protocol and token budgeting (`slim=true`)

### biosciences-architecture

Repository Analyzer Framework. Contains:
- `ra_orchestrators/` — 5 orchestrators (architecture, workspace, review, UX, base) totaling 3,068 lines
- `ra_agents/` — 14 JSON agent definitions across 3 domains (architecture, review, UX)
- `ra_tools/` — MCP registry, Pulumi (read-only), Figma (graceful fallback)
- `ra_output/` — timestamped analysis outputs

---

## Platform Layer

| Repo | Agent | Purpose | Package | LOC | Status |
|------|-------|---------|---------|-----|--------|
| biosciences-mcp | #3 MCP Platform Engineer | 12 FastMCP servers, 13 clients, 17 models, unified gateway | biosciences_mcp 0.1.0 | ~28K py (13K src + 15K test) | Complete |
| biosciences-memory | #4 Memory Engineer | Graphiti/Neo4j knowledge graph persistence, 9 MCP tools | biosciences_memory 0.1.0 | ~2.1K py | Complete |

### biosciences-mcp

The platform's central API layer. Contains:
- `src/biosciences_mcp/servers/` — 12 FastMCP servers + gateway
- `src/biosciences_mcp/clients/` — 13 async httpx clients (+ 1 ChEMBL SDK hybrid)
- `src/biosciences_mcp/models/` — 17 Pydantic v2 entity models, 22-key cross-reference registry
- `tests/` — 697+ tests (399 unit, 294 integration, 4 e2e)
- Deployed to FastMCP Cloud: `https://biosciences-mcp.fastmcp.app/mcp`

### biosciences-memory

Knowledge graph persistence. Contains:
- `src/biosciences_memory/server.py` — FastMCP server factory (9 tools)
- `src/biosciences_memory/services/` — queue service (per-group_id sequential processing), factories
- `src/biosciences_memory/models/` — 14 entity types (9 generic + 5 biosciences)
- Dual environment: Neo4j Aura (read-only, write-frozen) + Docker (active writes)

---

## Orchestration Layer

| Repo | Agent | Purpose | Package | LOC | Status |
|------|-------|---------|---------|-----|--------|
| biosciences-deepagents | #5 Deep Agents Engineer | LangGraph supervisor + 7 specialist subagents + React UI | biosciences-deepagents 0.1.0 | ~6.1K (py+ts) | Complete |
| biosciences-temporal | #7 Temporal Engineer | PydanticAI agents + Temporal.io durable workflows | biosciences_temporal 0.1.0 | ~1.9K py | Complete |
| biosciences-research | #6 Research Workflows | RAG evaluation (4 strategies) + 15 competency questions | biosciences-research 0.2.0 | ~3.6K py | Complete |

### biosciences-deepagents

Multi-agent research system. Contains:
- `apps/api/biosciences.py` — LangGraph supervisor with 7 specialist phases (ANCHOR, ENRICH, EXPAND, TRAVERSE_DRUGS, TRAVERSE_TRIALS, VALIDATE, PERSIST)
- `apps/web/` — React Next.js chat UI with streaming, subagent visualization, tool approval interrupts
- `apps/api/shared/mcp.py` — HTTP/Stdio MCP transport with per-service rate limiting
- Connects to biosciences-mcp gateway via HTTP, persists to Graphiti

### biosciences-temporal

Durable workflow execution. Contains:
- `src/biosciences_temporal/agents/` — 7 PydanticAI standalone agents (resolve, enrich, expand, drugs, trials, validate, cq14)
- `src/biosciences_temporal/temporal/` — Temporal activities, workflows, worker config
- Design: agents are testable standalone; Temporal wraps them for durability
- MCP transport: Stdio (subprocess) to avoid async cancel scope conflicts

### biosciences-research

RAG evaluation and competency questions. Contains:
- `src/` — Factory-pattern RAG library (retrievers, graph builders, state management)
- `scripts/` — Evaluation pipeline (ingest, inference, RAGAS metrics, publish to HuggingFace)
- `docs/competency-questions-catalog.md` — 15 CQs driving knowledge graph construction
- 4 retrieval strategies: naive, BM25, ensemble, Cohere rerank
- Makefile-driven: `make ingest`, `make eval`, `make validate`, `make publish-*`

---

## Validation & Support Layer

| Repo | Agent | Purpose | Package | LOC | Status |
|------|-------|---------|---------|-----|--------|
| biosciences-evaluation | #8 Quality & Skills | Quality gates: accuracy, completeness, provenance, latency, token efficiency | n/a (planned) | 0 | Not Started |
| biosciences-education | #9 Education & Workspace | Training materials, tutorials, onboarding guides | n/a (planned) | 0 | Not Started |
| biosciences-workspace-template | #9 Education & Workspace | Bootstrap scripts, workspace config templates | n/a (planned) | 0 | Not Started |
| platform-skills | #8 Quality & Skills | 2 scaffold commands + security-review skill (developer-facing) | n/a (skills only) | 0 py / ~1K md | Complete |
| marketplace | #8 Quality & Skills | 15 plugins in `.claude-plugin/` format for community distribution | n/a (manifests only) | 0 py | Complete |

### marketplace

Plugin marketplace packaging all platform assets:
- 12 MCP server plugins (one per database, each with `.mcp.json` + `plugin.json`)
- `domain-skills/` — 9 research skills copied from biosciences-skills
- `platform-tools/` — 2 scaffold commands + security-review from platform-skills
- `speckit/` — 9 SpecKit SDLC commands from biosciences-program
- Central registry: `.claude-plugin/marketplace.json`
