# Migration Status — Open Biosciences

## Wave Summary

| Wave | Name | Repos | Source | Status | Completion |
|------|------|-------|--------|--------|------------|
| 1 | Foundation | architecture, skills, program | lifesciences-research ADRs + skills | Complete | 100% |
| 1-ext | SpecKit | architecture → program | SpecKit artifacts consolidated | Complete | 100% |
| 2 | Platform | mcp, memory | lifesciences-research src/ + tests/ | Complete | 100% |
| 3 | Orchestration | deepagents, temporal | lifesciences-deepagents + lifesciences-temporal | Complete | 100% |
| 4 | Validation | evaluation, research, education, workspace-template | lifesciences-research docs/ | In Progress | ~40% |

## Wave 4 Detail

| Repo | Status | Notes |
|------|--------|-------|
| biosciences-research | Complete | RAG pipeline, 15 CQs, Makefile-driven evaluation |
| biosciences-evaluation | Not Started | Planned: rubrics, metrics, quality gates |
| biosciences-education | Not Started | Planned: tutorials, onboarding |
| biosciences-workspace-template | Not Started | Planned: bootstrap scripts, config templates |

## Predecessor Repos

Still functional as legacy references:

| Predecessor | Location | Migrated To |
|-------------|----------|-------------|
| lifesciences-research | `/home/donbr/graphiti-org/lifesciences-research` | biosciences-mcp, biosciences-architecture, biosciences-program |
| lifesciences-deepagents | `/home/donbr/ai2026/lifesciences-deepagents-worktrees/deepagents-0312-upgrade-spike` | biosciences-deepagents |
| lifesciences-temporal | `/home/donbr/graphiti-org/lifesciences-temporal` | biosciences-temporal |

## Post-Migration Completions

| Item | Issue | Status |
|------|-------|--------|
| Governance consolidation (architecture → program) | AGE-184 | Done |
| Governance references fixed across READMEs | AGE-220 | Done |
| Diagram standardization | AGE-219 | Done |
| Marketplace Cowork plugin alignment | AGE-217 | Done |
| platform-skills split | AGE-184 | Done |

## Remaining Work

1. **biosciences-evaluation** — Define rubrics, implement quality gates, create evaluation harness
2. **biosciences-education** — Write tutorials for Fuzzy-to-Fact, MCP usage, graph-builder, Temporal workflows
3. **biosciences-workspace-template** — Build bootstrap.sh, verify-env.sh, config templates
4. **Cross-repo integration testing** — End-to-end validation across all layers
