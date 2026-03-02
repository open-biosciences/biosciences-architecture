# Technology Stack — Open Biosciences

## Shared Conventions (All Repos)

| Convention | Standard |
|-----------|----------|
| Python | >=3.11 |
| Package manager | uv |
| Build backend | hatchling |
| Linting | ruff |
| Type checking | pyright |
| Models | Pydantic v2 |
| HTTP | httpx (async) |
| Testing | pytest with marker-based organization (`unit`, `integration`, `e2e`) |
| SDLC | SpecKit workflow (ADR-003) |
| API pattern | Fuzzy-to-Fact protocol (ADR-001 S3) |
| License | MIT |

## Core Technologies by Layer

### Foundation Layer

| Technology | Used In | Purpose |
|-----------|---------|---------|
| SpecKit | biosciences-program | Specification-driven SDLC (9 commands) |
| ADR framework | biosciences-program | Architecture Decision Records (6 ADRs) |
| Claude Agent SDK | biosciences-architecture | RA Framework orchestration (>=0.1.18) |

### Platform Layer

| Technology | Used In | Purpose |
|-----------|---------|---------|
| FastMCP | biosciences-mcp | MCP server framework (12 servers) |
| httpx | biosciences-mcp | Async HTTP clients (12 API integrations) |
| Pydantic v2 | biosciences-mcp, biosciences-memory | Entity models, validation, settings |
| Graphiti | biosciences-memory | Knowledge graph entity extraction + dedup |
| Neo4j | biosciences-memory | Graph database (Aura cloud + Docker local) |
| OpenAI | biosciences-memory | LLM for entity extraction (gpt-4.1-mini default) |

### Orchestration Layer

| Technology | Used In | Purpose |
|-----------|---------|---------|
| LangGraph | biosciences-deepagents | Supervisor-subagent orchestration |
| React / Next.js 16 | biosciences-deepagents | Streaming chat UI |
| PydanticAI | biosciences-temporal | Standalone agent definitions |
| Temporal.io | biosciences-temporal | Durable workflow execution |
| RAGAS | biosciences-research | RAG evaluation metrics |
| Qdrant | biosciences-research | Vector store for retrieval |
| Cohere | biosciences-research | Reranking (rerank-v3.5) |
| HuggingFace Hub | biosciences-research | Dataset publishing |

## External APIs (12 Life Sciences Databases)

| API | Auth | CURIE Format | Rate Limit | Key Tools |
|-----|------|-------------|------------|-----------|
| HGNC | None | `HGNC:1100` | Unlimited | search_genes, get_gene |
| UniProt | None | `UniProtKB:P38398` | Unlimited | search_proteins, get_protein |
| ChEMBL | None | `CHEMBL:25` | Moderate (frequent 500s) | search_compounds, get_compound, get_compounds_batch |
| Open Targets | None | `ENSG00000141510` | Unlimited (GraphQL) | search_targets, get_target, get_associations |
| STRING | None | `STRING:9606.ENSP*` | 1 req/s | search_proteins, get_interactions |
| BioGRID | Free key | Gene symbol | Moderate | search_genes, get_interactions |
| Ensembl | None | `ENSG*`, `ENST*` | 15 req/s | search_genes, get_gene, get_transcript |
| NCBI Entrez | Optional key | `NCBIGene:7157` | 3 req/s (10 with key) | search_genes, get_gene, get_pubmed_links |
| PubChem | None | `PubChem:CID2244` | 5 req/s | search_compounds, get_compound |
| IUPHAR/GtoPdb | None | `IUPHAR:2713` | Moderate | search_ligands, get_ligand |
| WikiPathways | None | `WP:WP534` | Unlimited | search_pathways, get_pathway |
| ClinicalTrials.gov | None | `NCT:00461032` | Moderate (Cloudflare) | search_trials, get_trial |

## Default LLM Models

| System | Model | Usage |
|--------|-------|-------|
| biosciences-deepagents | gpt-4o | Supervisor + 7 specialists |
| biosciences-temporal | gpt-4.1-mini | PydanticAI agents |
| biosciences-research | gpt-4.1-mini | RAG inference |
| biosciences-memory | gpt-4.1-mini | Graphiti entity extraction |

## Deployment Topology

| Component | Hosting | Endpoint |
|-----------|---------|----------|
| MCP Gateway | FastMCP Cloud | `https://biosciences-mcp.fastmcp.app/mcp` |
| Neo4j Aura | Neo4j Cloud | Aura free tier (write-frozen) |
| Neo4j Docker | Local Docker | `bolt://localhost:7687` |
| Graphiti Docker | Local Docker | `http://localhost:8002` |
| Temporal Server | Local Docker | `localhost:7233` (gRPC), `localhost:8233` (UI) |
| LangGraph Server | Local | LangGraph dev server (Studio UI) |
