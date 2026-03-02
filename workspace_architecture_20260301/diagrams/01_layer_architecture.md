# Layered Architecture — Open Biosciences

## Platform Layer Diagram

```mermaid
graph TB
    subgraph L1["Layer 1: Foundation"]
        PROG[biosciences-program<br/><i>ADRs, specs, SpecKit</i>]
        SKILLS[biosciences-skills<br/><i>9 domain skills</i>]
        ARCH[biosciences-architecture<br/><i>RA Framework</i>]
    end

    subgraph L2["Layer 2: Platform"]
        MCP[biosciences-mcp<br/><i>12 FastMCP servers + gateway</i><br/><i>697+ tests</i>]
        MEM[biosciences-memory<br/><i>Graphiti + Neo4j</i><br/><i>9 MCP tools</i>]
    end

    subgraph L3["Layer 3: Orchestration"]
        DEEP[biosciences-deepagents<br/><i>LangGraph supervisor</i><br/><i>7 specialists + React UI</i>]
        TEMP[biosciences-temporal<br/><i>PydanticAI + Temporal.io</i><br/><i>5-phase workflow</i>]
        RES[biosciences-research<br/><i>RAG eval + 15 CQs</i><br/><i>4 retrieval strategies</i>]
    end

    subgraph L4["Layer 4: Validation & Distribution"]
        EVAL[biosciences-evaluation<br/><i>Quality gates</i><br/><i>planned</i>]
        EDU[biosciences-education<br/><i>Tutorials</i><br/><i>planned</i>]
        WSTP[biosciences-workspace-template<br/><i>Bootstrap scripts</i><br/><i>planned</i>]
        PLAT[platform-skills<br/><i>2 scaffold cmds</i><br/><i>security-review</i>]
        MKT[marketplace<br/><i>15 .claude-plugins</i>]
    end

    %% Foundation provides to all
    PROG -->|ADRs, governance| L2
    PROG -->|SpecKit SDLC| L3
    SKILLS -->|domain skills| L3

    %% Platform serves orchestration
    MCP -->|12 API servers| DEEP
    MCP -->|stdio transport| TEMP
    MCP -->|graph-builder skill| RES
    MEM -->|graph persistence| DEEP
    MEM -->|graph persistence| RES

    %% Marketplace distributes
    MCP -.->|tool defs| MKT
    SKILLS -.->|skills copied| MKT
    PLAT -.->|commands copied| MKT
    PROG -.->|SpecKit copied| MKT

    %% Evaluation observes
    EVAL -.->|reads all| L3

    %% Styling
    style L1 fill:#e8f5e9,stroke:#2e7d32
    style L2 fill:#e3f2fd,stroke:#1565c0
    style L3 fill:#fff3e0,stroke:#e65100
    style L4 fill:#f3e5f5,stroke:#7b1fa2
    style EVAL fill:#fce4ec,stroke:#c62828
    style EDU fill:#fce4ec,stroke:#c62828
    style WSTP fill:#fce4ec,stroke:#c62828
```

## Layer Responsibilities

### Layer 1: Foundation (Root Providers)
- **No upstream dependencies** — consumed by everything
- biosciences-program: governance, ADRs, specs, migration coordination
- biosciences-skills: domain-specific research skills
- biosciences-architecture: Repository Analyzer Framework (analysis tooling)

### Layer 2: Platform (Infrastructure)
- **Depends on:** Layer 1 (ADR compliance, schema definitions)
- biosciences-mcp: 12 life sciences API wrappers in a unified gateway
- biosciences-memory: Graphiti knowledge graph with Neo4j persistence

### Layer 3: Orchestration (Applications)
- **Depends on:** Layers 1 + 2 (skills, MCP tools, graph persistence)
- biosciences-deepagents: interactive multi-agent research (LangGraph + React)
- biosciences-temporal: durable research pipelines (PydanticAI + Temporal)
- biosciences-research: RAG evaluation and competency question workflows

### Layer 4: Validation & Distribution
- **Depends on:** Layers 1-3 (observational, no runtime coupling)
- biosciences-evaluation: quality measurement (planned)
- biosciences-education: training content (planned)
- biosciences-workspace-template: bootstrap automation (planned)
- platform-skills: developer-facing scaffold commands
- marketplace: community-facing plugin distribution
