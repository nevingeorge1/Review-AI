# ReviewAI — System Architecture & Design Specification

## 1. System Overview

**ReviewAI** is an enterprise-grade, privacy-first intelligent code review and engineering insights assistant. It combines deterministic static code analysis with large language model (LLM) contextual reasoning to detect bugs, security vulnerabilities, code smells, and performance bottlenecks, generating actionable developer feedback.

### Core Architectural Philosophy

```
+-------------------------------------------------------------------------+
|                              SOURCE CODE                                |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                  PREPROCESSING & INPUT SANITIZATION                     |
|         (Line count, payload size validation, language detection)        |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                  AST INTELLIGENCE & STRUCTURAL EXTRACTION               |
|      (Safe AST Visitor, Functions, Classes, Calls, Complexity Metrics)  |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                  STATIC CODE ANALYSIS ENGINE (Deterministic)            |
|       (AST Rules Engine, Ruff Linter, Bandit Security Scanner)          |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                EVIDENCE NORMALIZATION & DEDUPLICATION                   |
|     (Multi-tool finding normalization, provenance merging, severities)  |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                     LLM REASONING LAYER (Contextual)                    |
|   (ContextBuilder, PromptBuilder, Local Ollama Qwen2.5-Coder / Mock,    |
|    OutputParser with Line Clamping, Static-Only Fallback Mode)          |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                  FINDING FUSION & EVIDENCE CORRELATION                  |
|     (Multi-source fusion, elevation to HYBRID, severity precedence)     |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                  PRIORITIZATION & CODE HEALTH SCORING                   |
|     (Impact ranking, 0-100 score formula, category sub-scores, grades)  |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                     API / WEB UI / REPORT PRESENTATION                  |
|                 (FastAPI REST endpoints, React Dashboard)               |
+-------------------------------------------------------------------------+
```

---

## 2. Layered Architecture & Separation of Concerns

ReviewAI enforces strict Clean Architecture boundaries to ensure modularity, testability, and technology independence:

```
┌────────────────────────────────────────────────────────┐
│                      API Layer                         │
│   (FastAPI routes, request validation, DTOs, DI)       │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                  Service Orchestration                 │
│         (ReviewService, StorageRepository contracts)    │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                      ReviewEngine                      │
│   (Pipeline orchestrator, stage telemetry, lifecycle)  │
└───────┬───────────────────┬───────────────────┬────────┘
        │                   │                   │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼────────┐
│ Preprocessor  │   │ Static Engine │   │   LLM Service  │
│ & AST Visitor │   │ Ruff/Bandit/AST   │ Context/Prompts│
└───────┬───────┘   └───────┬───────┘   └───────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │      FindingFusion & Prioritizer      │
        │ - Correlate static and LLM findings   │
        │ - Severity & confidence precedence    │
        │ - Prioritize Critical/Security first  │
        └───────────────────┬───────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │            ScoreCalculator            │
        │ - 0-100 overall score & sub-scores    │
        │ - Letter grade assignment (A+ to F)   │
        └───────────────────┬───────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │            Domain Models              │
        │ (ReviewFinding, QualityScore, Summary)│
        └───────────────────────────────────────┘
```

---

## 3. Module 6: Hybrid Review Engine & Quality Scoring

### 3.1. ReviewEngine Workflow

```
AnalysisRequest (Source + Language + Options)
                     │
                     ▼
[Stage 1: Preprocessor] ──> Line count & byte check, AST extraction, Syntax validation
                     │
                     ▼
[Stage 2: Static Engine] ──> Ruff, Bandit, 15 AST Rules (Failure Isolation)
                     │
                     ▼
[Stage 3: LLM Layer]    ──> Local Ollama (Qwen2.5-Coder) or Static-Only Fallback
                     │
                     ▼
[Stage 4: FindingFusion] ──> Correlate findings, resolve severity, elevate to HYBRID
                     │
                     ▼
[Stage 5: Prioritizer]  ──> Rank: Critical/Security -> Bugs -> Perf -> Maint -> Style
                     │
                     ▼
[Stage 6: Scorer]       ──> 0-100 Score = 0.3*Sec + 0.3*Rel + 0.2*Maint + 0.1*Perf + 0.1*Style
                     │
                     ▼
AnalysisResponse (Findings + Summary + QualityScore + Stage Timings)
```

### 3.2. Code Health Score Formula
$$\text{Overall Score} = 0.30 \times S_{\text{sec}} + 0.30 \times S_{\text{rel}} + 0.20 \times S_{\text{maint}} + 0.10 \times S_{\text{perf}} + 0.10 \times S_{\text{style}}$$
- **Letter Grades**: `A+` ($\ge 95$), `A` ($\ge 90$), `B` ($\ge 80$), `C` ($\ge 70$), `D` ($\ge 60$), `F` ($< 60$).
