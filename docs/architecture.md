# DataMint Architecture

## Overview

DataMint is a synthetic data generation toolkit focused on two use cases: (1) generating "golden datasets" for LLM evaluation, and (2) generating adversarial prompts for red-teaming. It uses template-based generation and statistical methods — no LLM required.

## C4 Diagrams

### Level 1: System Context

```mermaid
graph TB
    User["Developer / QA Engineer"]
    DataMint["DataMint<br/>Synthetic Data Toolkit"]
    Source["Source Documents<br/>(text files)"]
    Output["Generated Datasets<br/>(JSON / JSONL / CSV)"]
    Eval["Eval Framework<br/>(DeepEval / Promptfoo)"]

    User -->|"CLI / Python API"| DataMint
    Source -->|"input text"| DataMint
    DataMint -->|"synthetic data"| Output
    Output -->|"golden dataset"| Eval

    style DataMint fill:#10b981,stroke:#059669,color:#fff
```

### Level 2: Container Diagram

```mermaid
graph TB
    subgraph DataMint["DataMint"]
        CLI["CLI<br/>(click)"]
        QAGen["QA Generator"]
        AdvGen["Adversarial Generator"]
        TabGen["Tabular Generator"]
        Export["Exporter<br/>(JSON/JSONL/CSV)"]
    end

    CLI --> QAGen
    CLI --> AdvGen
    CLI --> TabGen
    QAGen --> Export
    AdvGen --> Export
    TabGen --> Export

    style DataMint fill:#ecfdf5,stroke:#10b981
    style QAGen fill:#10b981,color:#fff
    style AdvGen fill:#ef4444,color:#fff
    style TabGen fill:#3b82f6,color:#fff
```

### Sequence Diagram: QA Generation

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant QAGen as QA Generator
    participant Export as Exporter

    User->>CLI: datamint generate --preset qa --source doc.txt
    CLI->>QAGen: generate(source_text, count=10)
    QAGen->>QAGen: split text into chunks
    QAGen->>QAGen: apply question templates per chunk
    QAGen->>QAGen: generate answer from chunk context
    QAGen-->>CLI: List[QAPair]
    CLI->>Export: export(pairs, format="json")
    Export-->>User: golden_dataset.json
```

## Design Decisions

### Template-based vs. LLM-based Generation

**Chose:** Template-based question generation with algorithmic answer extraction.

**Why:** Zero external dependencies, reproducible output, works offline. An LLM-powered mode can be added as an optional enhancement.

**Tradeoff:** Lower diversity and naturalness compared to LLM-generated data. Sufficient for automated eval pipelines where consistency matters more than creativity.

### Adversarial Prompt Categories

Categories are based on OWASP LLM Top 10 and common red-teaming taxonomies. Templates are parameterized and composable, allowing combinatorial generation.

## Extension Points

1. Custom question templates via config
2. Custom adversarial prompt categories
3. Plugin system for LLM-backed generation (roadmap)
4. HuggingFace Dataset export format (roadmap)
