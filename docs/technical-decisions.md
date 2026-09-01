# ReviewAI — Architecture Decision Records (ADRs)

This document records the foundational technical and architectural decisions made for the ReviewAI platform.

---

## ADR-001: Monorepo Architecture

### Context
ReviewAI consists of a Python FastAPI backend, a React/TypeScript web UI, an automated evaluation pipeline, sample code repositories, and documentation.

### Decision
Adopt a clean monorepo layout:
- `backend/`: Application services, models, analysis, and API.
- `frontend/`: Single-page developer application.
- `evaluation/`: Benchmark datasets, ground-truth suites, metric calculation.
- `notebooks/`: Exploratory workflows and Google Colab demonstrations.
- `docs/`: Technical specifications, ADRs, security, and setup guides.
- `samples/`: Curated code test fixtures with known issues.

---

## ADR-002: Local-First LLM Architecture with Ollama & Qwen2.5-Coder

### Context
Code review tools often process sensitive intellectual property. Relying exclusively on proprietary cloud APIs raises privacy concerns and cost barriers.

### Decision
Standardize on a **Local-First LLM Architecture** powered by Ollama and open-source models (specifically the `Qwen2.5-Coder` family, e.g., `7b-instruct`).

---

## ADR-003: Static-First Evidence with LLM Synthesis (Hybrid Engine)

### Context
Pure LLM code reviewers suffer from hallucinations, missed syntax subtleties, and non-deterministic line numbers. Pure static linters lack contextual explanation, priority scoring, and semantic fix synthesis.

### Decision
Implement a **hybrid two-stage review pipeline**:
1. Static analysis tools (Python AST, Ruff, Bandit) run deterministically to discover factual evidence.
2. The LLM receives normalized static evidence + raw source code to provide prioritization, context, false-positive filtering, and actionable suggested fixes.

---

## ADR-004: Static-Only Fallback & Graceful Degradation

### Context
In resource-constrained environments (e.g., CI runners, developer laptops without GPU, offline instances), an LLM provider may be unavailable or slow.

### Decision
ReviewAI must support a first-class **Static-Only Fallback Mode**. If Ollama is offline or `ENABLE_LLM=false`, the system completes the review using static analysis findings alone without failing the request.

---

## ADR-005: Domain Model Abstractions & Pydantic v2

### Context
Data consistency across analysis stages, storage, and API responses requires strong runtime validation and serialization.

### Decision
Use **Pydantic v2** domain models strictly separated from database or framework specifics. All findings conform to normalized `StaticFinding` and `ReviewFinding` schemas.

---

## ADR-006: Repository Pattern for Storage

### Context
Module 1 must establish a clean foundation without introducing heavy infrastructure dependencies (like PostgreSQL or ORMs).

### Decision
Define a `ReviewRepository` interface. In Module 1, use an in-memory repository implementation while maintaining architectural readiness for SQLite and PostgreSQL in subsequent modules.

---

## ADR-007: API Versioning, Schemas (DTOs), and Contract Segregation

### Context
API controllers need clear boundaries separating external client data transfer objects (DTOs) from core domain entities and database models.

### Decision
- Mount all application APIs under the versioned prefix `/api/v1/`.
- Provide root `/health` and versioned `/api/v1/health` probes.
- Structure DTOs in `backend/app/schemas/` (`ReviewCreateRequest`, `ReviewResponse`, `ReviewListResponse`, `HealthResponse`, `ErrorResponse`).

---

## ADR-008: Service-Layer Architecture & Lifespan Management

### Context
FastAPI route functions should remain lightweight controllers and must not contain direct business logic, file validation rules, or persistence code.

### Decision
- Introduce `ReviewService` in `backend/app/services/review_service.py` to encapsulate business validations, ID generation, and repository coordination.
- Use FastAPI dependency injection (`backend/app/api/deps.py`) to inject repositories and services into route handlers.
- Use the modern `@asynccontextmanager` FastAPI `lifespan` handler for clean application startup and shutdown lifecycle management.

---

## ADR-009: Static AST Representation vs Dynamic Code Execution

### Context
Analyzing user-submitted code could theoretically involve importing modules, executing code under observation, or running dynamic sandboxes. However, submitted code in review tools is untrusted and may contain hostile payloads, infinite loops, or system modification attempts.

### Decision
ReviewAI enforces a strict invariant: **Submitted code is treated exclusively as static text DATA and is NEVER executed, evaluated, imported, or run dynamically.**
- AST parsing is performed directly via `ast.parse(source_text)`.
- No dynamic imports (`__import__`, `importlib`), no `eval()`, and no `exec()`.

---

## ADR-010: Single-Pass Structural Extraction & Cyclomatic Complexity Formula

### Context
Static analyzers and LLMs need structured code context (functions, classes, calls, imports, control flow, nesting depth, line counts, and complexity metrics). Multiple AST traversals degrade performance on large submissions.

### Decision
- Implement `PythonASTVisitor(ast.NodeVisitor)` to extract all structural records and control flow counters in a **single visitor pass**.
- Standardize on an explicit McCabe-derived cyclomatic complexity calculation:
  $$\text{Complexity} = 1 + \sum(\text{If}) + \sum(\text{For}) + \sum(\text{While}) + \sum(\text{Except}) + \sum(\text{With}) + \sum(\text{Assert}) + \sum(\text{BoolOp Operands} - 1) + \sum(\text{Comprehensions})$$

---

## ADR-011: Multi-Tool Static Analysis Orchestration with Failure Isolation

### Context
Different static analyzers have distinct strengths (Ruff for lint/style, Bandit for security heuristics, custom AST rules for project-specific signals). External CLI binaries may be missing, misconfigured, or slow.

### Decision
- Implement `StaticAnalysisEngine` orchestrating `ASTRuleAnalyzer`, `RuffAnalyzer`, and `BanditAnalyzer`.
- Wrap each tool execution with strict subprocess isolation, isolated temporary files with 0600 permissions, and independent timeout guards (`STATIC_ANALYZER_TIMEOUT`).
- Ensure failure isolation: If Ruff or Bandit fails or is missing, the built-in AST rule analyzer completes normally without failing the user request.

---

## ADR-012: Finding Deduplication & Multi-Tool Provenance Preservation

### Context
Running multiple static analysis tools against the same codebase inevitably produces overlapping findings for the same underlying issue (e.g. Bandit B307 and AST RULE-001 both flagging `eval`). Presenting duplicate warnings degrades developer experience.

### Decision
- Implement `deduplicate_and_merge_static_findings` in `backend/app/analyzers/deduplicator.py`.
- Match findings based on Category + Line Proximity ($|line_1 - line_2| \le 1$) + Semantic Rule Intent.
- Merge overlapping findings by preserving multi-tool provenance (`analyzer_name = "bandit,ast_rules"`), retaining the highest severity assessment, and selecting the most descriptive message.
- Strictly keep distinct issues at the same line (e.g. style vs security) separate.

---

## ADR-013: Context and Prompt Engineering Strategy for Grounded Review

### Context
Generic LLM code review prompts produce noisy, conversational, and hallucinated comments. Grounding the LLM with deterministic static evidence and numbered lines dramatically improves precision.

### Decision
- Implement `ReviewContextBuilder` producing structured `ReviewContext` (schema v1.0).
- Implement `ReviewPromptBuilder` generating numbered source code and structured static evidence.
- Enforce the **Untrusted Data Invariant**: explicitly instruct the model to treat source comments, docstrings, and string literals as untrusted data and ignore prompt injection attempts.

---

## ADR-014: LLM Output Validation & Defensive Line Clamping

### Context
LLM responses may include conversational preambles, markdown formatting fences, hallucinated line numbers outside the file range, or invalid category strings.

### Decision
- Implement `LLMOutputParser` using regex fence stripping and strict Pydantic model validation (`LLMRawResponsePayload`).
- Validate line numbers against source file length: clamp $1 \le \text{line\_number} \le \text{total\_lines}$ and safely omit out-of-range line references rather than creating phantom lines.
- Map unknown categories/severities to safe defaults (`Category.BUG`, `Severity.MEDIUM`).

---

## ADR-015: Finding Fusion, Severity Precedence, and Provenance Policy

### Context
When static analyzers and LLMs inspect the same submission, both may detect the same underlying flaw with slightly different wording or severities.

### Decision
- Implement `FindingFusion` in `backend/app/review/fusion.py`.
- Elevate corroborated findings to `DetectionSource.HYBRID` with elevated confidence ($0.96 - 0.98$).
- Enforce severity precedence: `max_severity(static, llm)`. Deterministic static security evidence cannot be downgraded by an LLM.
- Retain complete provenance in `detected_by` and `supporting_evidence`.

---

## ADR-016: Explainable Code Health Scoring & Category Weighting Formula

### Context
Code review tools often output opaque scores. Developers require an explainable score grounded in actionable findings.

### Decision
- Implement `ScoreCalculator` in `backend/app/review/scorer.py`.
- Base score of 100.0 points per category, deducting points based on finding severity and confidence.
- Weighted aggregate score: Security (30%), Reliability (30%), Maintainability (20%), Performance (10%), Style (10%).
- Assign intuitive letter grades (`A+` through `F`).
