# ReviewAI — Hybrid Review Engine & Quality Scoring Specification

## 1. Executive Summary

The **Hybrid Review Engine** (Module 6) is the master orchestration and intelligence fusion layer of ReviewAI. It integrates deterministic static code analysis with local LLM reasoning, correlates multi-source evidence, enforces severity precedence, prioritizes critical findings, and computes an explainable 0–100 code health score.

---

## 2. Review Engine Pipeline Architecture

```
                    SOURCE CODE SUBMISSION
                              │
                              ▼
                 ┌─────────────────────────┐
                 │       ReviewEngine      │
                 └────────────┬────────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       ▼                      ▼                      ▼
 [Preprocessing]      [Static Analysis]      [Context Builder]
 (AST & Metrics)     (Ruff, Bandit, AST)     (Prompt Assembly)
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              ▼
                 ┌─────────────────────────┐
                 │    LLM Reasoning Layer  │
                 │ (Ollama / Qwen2.5-Coder)│
                 │ *Fallback if offline*   │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │      FindingFusion      │
                 │ - Multi-tool correlation│
                 │ - Elevate to HYBRID     │
                 │ - Severity resolution   │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │    FindingPrioritizer   │
                 │ (Rank: Sec > Bug > ...) │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │     ScoreCalculator     │
                 │ (0-100 Score & Grades)  │
                 └────────────┬────────────┘
                              │
                              ▼
                     AnalysisResponse
```

---

## 3. Review Modes

ReviewAI operates in two distinct, deterministic modes:

| Review Mode | Trigger Condition | Characteristics |
| :--- | :--- | :--- |
| **`HYBRID`** | `ENABLE_LLM=true` and LLM provider is operational | Fuses static evidence with LLM contextual reasoning, elevates corroborated findings to `HYBRID`, provides AI executive summary and suggested code fixes. |
| **`STATIC_ONLY`** | `ENABLE_LLM=false` or LLM provider is offline/timed out | Delivers verified deterministic static findings, computes code health score, generates deterministic summary without failing the request. |

---

## 4. Finding Fusion & Provenance Policy

When multi-source analysis is performed, findings are correlated and fused using strict heuristics:

### 4.1. Corroboration Criteria
Two findings (one static, one LLM) are merged if:
1. They share the same `Category` (e.g. both `SECURITY` or both `BUG`).
2. They target overlapping lines ($|line_{static} - line_{llm}| \le 2$).
3. They share semantic keywords or rule intent (`eval`, `exec`, `os.system`, `subprocess`, `pickle`, `sql`, `credential`, `mutable`, etc.).

### 4.2. Fusion Outcome
- **Detection Source**: Elevated to `DetectionSource.HYBRID`.
- **Analyzer Provenance**: Consolidated list (e.g. `detected_by = ["bandit", "ast_rules", "llm"]`).
- **Severity Precedence**: Resolves to `max_severity(static, llm)`. **Invariant**: Deterministic static security evidence cannot be downgraded by an LLM.
- **Confidence Elevation**: Elevated to $0.96 - 0.98$ (`confidence_level = "HIGH"`).
- **Supporting Evidence**: All raw tool messages and snippets are preserved in `supporting_evidence`.

---

## 5. Finding Prioritization Hierarchy

Findings are sorted deterministically in descending order of engineering impact:
1. **Severity**: `CRITICAL` $\to$ `HIGH` $\to$ `MEDIUM` $\to$ `LOW` $\to$ `INFO`
2. **Category**: `SECURITY` $\to$ `BUG` $\to$ `PERFORMANCE` $\to$ `MAINTAINABILITY` $\to$ `STYLE`
3. **Confidence**: Higher confidence findings appear before lower confidence findings.
4. **Source Location**: Top-to-bottom within file.

---

## 6. Code Health Scoring Formula

ReviewAI computes a transparent, explainable 0–100 code health score:

### 6.1. Category Deduction Weights
Base deductions per finding severity:
- `CRITICAL`: 25.0 points
- `HIGH`: 15.0 points
- `MEDIUM`: 8.0 points
- `LOW`: 3.0 points
- `INFO`: 0.5 points

$$\text{Category Penalty} = \sum_{i} \left( \text{Weight}_i \times \text{Confidence}_i \right)$$

$$\text{SubScore}_{\text{cat}} = \max\left(0.0, 100.0 - \text{Category Penalty}\right)$$

### 6.2. Overall Health Score Calculation
Weighted aggregate across category sub-scores:

$$\text{Overall Score} = 0.30 \times S_{\text{sec}} + 0.30 \times S_{\text{rel}} + 0.20 \times S_{\text{maint}} + 0.10 \times S_{\text{perf}} + 0.10 \times S_{\text{style}}$$

### 6.3. Letter Grade Assignment
- **A+**: $95.0 - 100.0$
- **A**: $90.0 - 94.9$
- **B**: $80.0 - 89.9$
- **C**: $70.0 - 79.9$
- **D**: $60.0 - 69.9$
- **F**: $< 60.0$

---

## 7. Suggested Fix Safety Invariants

> [!CAUTION]
> **Safety Invariant**: Suggested code replacements generated by static rules or LLMs are **suggestions only**.
> - ReviewAI **never** modifies source files automatically.
> - ReviewAI **never** executes suggested fixes.
> - All suggested fixes must be reviewed and tested by human engineers before merging.

---

## 8. Known Limitations

- **Single-File Scope**: Single-file reviews cannot guarantee the absence of global cross-repository architectural regressions.
- **Heuristic Nature**: The Code Health Score is an explainable engineering heuristic designed for directional code quality feedback, not an absolute statistical guarantee.
