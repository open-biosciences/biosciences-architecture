# Primary Data Flow — Open Biosciences

## Research Query Flow

The primary data flow through the platform follows the Fuzzy-to-Fact protocol across all orchestration systems.

```mermaid
sequenceDiagram
    participant User
    participant Agent as Agent System<br/>(deepagents / temporal / research)
    participant Gateway as biosciences-mcp<br/>FastMCP Gateway
    participant APIs as External APIs<br/>(12 databases)
    participant Graph as biosciences-memory<br/>Graphiti + Neo4j

    User->>Agent: Research query<br/>"What drugs target BRCA1?"

    Note over Agent: Phase 1: ANCHOR (Fuzzy Discovery)
    Agent->>Gateway: search_genes(query="BRCA1")
    Gateway->>APIs: HGNC REST API
    APIs-->>Gateway: Ranked candidates
    Gateway-->>Agent: [{name: "BRCA1", id: "HGNC:1100", score: 0.99}]

    Note over Agent: Phase 2: ENRICH (Strict Lookup)
    Agent->>Gateway: get_gene(hgnc_id="HGNC:1100")
    Gateway->>APIs: HGNC REST API
    APIs-->>Gateway: Full gene record
    Gateway-->>Agent: Gene entity with cross_references

    Agent->>Gateway: get_protein(uniprot_id="UniProtKB:P38398")
    Gateway->>APIs: UniProt REST API
    APIs-->>Gateway: Protein record
    Gateway-->>Agent: Protein entity

    Note over Agent: Phase 3: EXPAND (Interactions)
    Agent->>Gateway: get_interactions(protein_id="STRING:9606.ENSP...")
    Gateway->>APIs: STRING API
    APIs-->>Gateway: Interaction network
    Gateway-->>Agent: Interaction edges

    Note over Agent: Phase 4: TRAVERSE (Drugs + Trials)
    Agent->>Gateway: search_compounds(query="BRCA1 inhibitor")
    Gateway->>APIs: ChEMBL API
    APIs-->>Gateway: Drug candidates
    Gateway-->>Agent: Compound entities

    Agent->>Gateway: search_trials(query="BRCA1")
    Gateway->>APIs: ClinicalTrials.gov
    APIs-->>Gateway: Trial matches
    Gateway-->>Agent: Trial entities

    Note over Agent: Phase 5: VALIDATE
    Agent->>Agent: Cross-source verification

    Note over Agent: Phase 6: PERSIST
    Agent->>Graph: add_memory(entities, group_id="cq14")
    Graph->>Graph: Entity dedup + relationship extraction
    Graph-->>Agent: Persisted

    Agent-->>User: Structured research report
```

## Three Orchestration Paths

The same Fuzzy-to-Fact flow is implemented in three different systems, each optimized for a different use case:

```mermaid
graph LR
    subgraph Interactive["Interactive Research"]
        DEEP[biosciences-deepagents<br/><i>LangGraph supervisor</i>]
        UI[React Chat UI<br/><i>streaming + tool approval</i>]
        DEEP --- UI
    end

    subgraph Durable["Durable Pipelines"]
        TEMP[biosciences-temporal<br/><i>PydanticAI agents</i>]
        TIO[Temporal.io<br/><i>crash recovery + retries</i>]
        TEMP --- TIO
    end

    subgraph Evaluation["RAG Evaluation"]
        RES[biosciences-research<br/><i>4 retrieval strategies</i>]
        RAGAS[RAGAS Metrics<br/><i>faithfulness, relevancy</i>]
        RES --- RAGAS
    end

    MCP[biosciences-mcp<br/>12 API servers]
    MEM[biosciences-memory<br/>Knowledge Graph]

    DEEP -->|HTTP gateway| MCP
    TEMP -->|Stdio transport| MCP
    RES -->|graph-builder skill| MCP

    DEEP -->|persist_to_graphiti| MEM
    RES -->|group_id namespaces| MEM

    style Interactive fill:#fff3e0,stroke:#e65100
    style Durable fill:#e8f5e9,stroke:#2e7d32
    style Evaluation fill:#e3f2fd,stroke:#1565c0
    style MCP fill:#bbdefb,stroke:#1565c0,stroke-width:3px
    style MEM fill:#bbdefb,stroke:#1565c0,stroke-width:2px
```

| Path | System | Use Case | LLM | Transport |
|------|--------|----------|-----|-----------|
| Interactive | biosciences-deepagents | Ad-hoc research with human-in-the-loop | gpt-4o | HTTP gateway |
| Durable | biosciences-temporal | Reproducible pipelines with crash recovery | gpt-4.1-mini | Stdio subprocess |
| Evaluation | biosciences-research | RAG strategy comparison + quality measurement | gpt-4.1-mini | Via graph-builder skill |
