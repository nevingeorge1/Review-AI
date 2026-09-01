# ReviewAI — Static Analysis & Evidence Engine Specification

## 1. Executive Summary

The **Static Analysis & Evidence Engine** (Module 4) is the deterministic factual foundation of ReviewAI. It orchestrates multiple specialized static inspection tools (Ruff, Bandit, and 15 custom AST rules) into a unified, deduplicated evidence stream.

---

## 2. Multi-Tool Architecture & Roles

```
                    SOURCE CODE
                         │
                         ▼
                  PREPROCESSOR
                         │
                         ▼
                 ┌───────────────┐
                 │ STATIC ENGINE │
                 └───────┬───────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
        RUFF           BANDIT        AST RULES
     (Lint/Style)    (Security)    (Custom Context)
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                FINDING NORMALIZER
                         │
                         ▼
                 EVIDENCE LAYER
                         │
                         ▼
              DEDUPLICATION / MERGE
                         │
                         ▼
              NORMALIZED FINDINGS
```

| Tool | Focus Area | Strengths | Execution Mechanism |
| :--- | :--- | :--- | :--- |
| **Ruff** | Code Style, Formatting, Pyflakes Bugs | Sub-millisecond speed, standard Python conventions | Safe subprocess (`ruff check --output-format=json`) |
| **Bandit** | Common Security Vulnerabilities | Broad AST security heuristics (B101–B703) | Safe subprocess (`bandit -f json -q`) |
| **Custom AST Rules** | Deep Contextual Signals | Low false-positive rate, custom complexity, SQL & command signals | In-process Python AST traversal (100% deterministic) |

---

## 3. Custom AST Rule Catalog

ReviewAI implements 15 high-value custom AST inspection rules:

| Rule ID | Title | Category | Severity | Detection Target |
| :--- | :--- | :--- | :---: | :--- |
| `RULE-001` | Dangerous dynamic execution: `eval()` | `SECURITY` | `HIGH` | Direct invocations of `eval()` |
| `RULE-002` | Dangerous dynamic execution: `exec()` | `SECURITY` | `HIGH` | Direct invocations of `exec()` |
| `RULE-003` | Dynamic module import: `__import__()` | `SECURITY` | `MEDIUM` | Invocations of `__import__()` |
| `RULE-004` | Shell command execution: `os.system()` | `SECURITY` | `HIGH` | Invocations of `os.system()` |
| `RULE-005` | Unsafe subprocess shell execution | `SECURITY` | `HIGH` | `subprocess.*` with `shell=True` or formatted string commands |
| `RULE-006` | Unsafe pickle deserialization | `SECURITY` | `HIGH` | `pickle.loads()`, `pickle.load()` |
| `RULE-007` | Broad exception handling | `MAINTAINABILITY` | `LOW` | `except Exception:` |
| `RULE-008` | Mutable default function arguments | `BUG` | `HIGH` | `def f(items=[])`, `def f(d={})`, `def f(s=set())` |
| `RULE-009` | Bare except statement | `MAINTAINABILITY` | `MEDIUM` | `except:` without type |
| `RULE-010` | Excessive function complexity | `MAINTAINABILITY` | `MEDIUM` | Cyclomatic complexity > `MAX_FUNCTION_COMPLEXITY` |
| `RULE-011` | Excessive nesting depth | `MAINTAINABILITY` | `LOW` | Block depth > `MAX_NESTING_DEPTH` |
| `RULE-012` | Too many function parameters | `MAINTAINABILITY` | `LOW` | Parameter count > `MAX_FUNCTION_PARAMETERS` |
| `RULE-013` | Potential hard-coded credentials | `SECURITY` | `HIGH` | Secret variable names (`api_key`, `secret`) with token strings |
| `RULE-014` | Potential SQL injection | `SECURITY` | `HIGH` | Dynamic concatenation/formatting in `cursor.execute()` |
| `RULE-015` | Inefficient nested iteration | `PERFORMANCE` | `MEDIUM` | Nested loops over collections |

---

## 4. Severity & Category Normalization

| Source Tool Finding | Normalized Category | Normalized Severity |
| :--- | :--- | :---: |
| Bandit `HIGH` | `SECURITY` | `HIGH` |
| Bandit `MEDIUM` | `SECURITY` | `MEDIUM` |
| Bandit `LOW` | `SECURITY` | `LOW` |
| Ruff `F` (Pyflakes syntax/undefined) | `BUG` | `HIGH` / `MEDIUM` |
| Ruff `E` / `W` (pycodestyle) | `STYLE` | `LOW` |
| Ruff `B` (flake8-bugbear) | `BUG` / `MAINTAINABILITY` | `MEDIUM` |
| Ruff `PERF` / `C4` | `PERFORMANCE` | `LOW` |
| Ruff `SIM` / `UP` | `MAINTAINABILITY` | `INFO` |
| Custom AST Rules | Defined per rule schema | Defined per rule schema |

---

## 5. Finding Deduplication & Merging

When multiple tools detect the same underlying issue on the same line:
1. **Deduplication Criteria**: Same category + line proximity ($|line_1 - line_2| \le 1$) + matching semantic keyword / rule intent.
2. **Provenance Preservation**: Consolidated analyzer provenance is recorded (e.g. `analyzer_name = "bandit,ast_rules"`).
3. **Severity Resolution**: The higher severity assessment is preserved.
4. **Different Issues at Same Line**: Unrelated issues (e.g. a style warning on line 10 and a security vulnerability on line 10) are strictly kept separate.

---

## 6. Failure Isolation & Static-Only Operation

1. **Tool Independence**: If Ruff or Bandit is uninstalled or times out, the built-in AST rule engine continues uninterrupted.
2. **Static-Only Operation**: The entire static analysis pipeline executes without any dependency on external LLMs or cloud endpoints.

---

## 7. Explicit Technical Limitations

> [!IMPORTANT]
> **Static Analysis Boundaries**:
> - **Zero Runtime Execution**: ReviewAI does not execute user code; runtime state, dynamic monkey-patching, and external API responses cannot be inspected statically.
> - **Heuristic Nature of Rules**: Static signals (e.g. SQL string concatenation) represent high-risk code patterns, not guaranteed exploitability.
> - **No Full Dynamic Taint Tracking**: Cross-file or runtime taint flow requires dynamic instrumentation or heavyweight semantic graphs beyond the single-file static scope.
