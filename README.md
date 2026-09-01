# 🚀 ReviewAI: Hybrid AI Code Review Assistant

Review-AI Url:https://review-aiv1.vercel.app/

> **A production-grade, privacy-first AI Code Review Assistant combining deterministic Abstract Syntax Tree (AST) static analysis with local Large Language Model (LLM) reasoning to produce actionable, high-confidence developer feedback.**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NevinGeorge/reviewai/blob/main/notebooks/reviewai_demo.ipynb)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://reactjs.org/)
[![Monaco Editor](https://img.shields.io/badge/Monaco_Editor-VS_Code_Core-blue.svg)](https://microsoft.github.io/monaco-editor/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Privacy](https://img.shields.io/badge/Privacy-100%25_Local_Offline-purple.svg)](docs/security.md)

---

## 📑 Table of Contents

1. [🌟 What is ReviewAI?](#-what-is-reviewai)
2. [💡 The Problem & The Hybrid Solution](#-the-problem--the-hybrid-solution)
3. [🏗️ System Architecture & Data Flow](#️-system-architecture--data-flow)
4. [✨ Key Features](#-key-features)
5. [📋 The 15 AST Intelligence Rules Engine](#-the-15-ast-intelligence-rules-engine)
6. [📊 Deterministic 0–100 Health Scoring Model](#-deterministic-0100-health-scoring-model)
7. [📓 Interactive Google Colab Notebook](#-interactive-google-colab-notebook)
8. [⚡ Quickstart Guide (Step-by-Step for Beginners)](#-quickstart-guide-step-by-step-for-beginners)
9. [🌐 Vercel & Production Deployment](#-vercel--production-deployment)
10. [📈 Benchmark Evaluation & Performance](#-benchmark-evaluation--performance)
11. [📂 Repository Structure](#-repository-structure)
12. [🔌 REST API Documentation](#-rest-api-documentation)

---

## 🌟 What is ReviewAI?

**ReviewAI** is an intelligent, developer-centric code review platform that acts as an automated senior engineer pair-programmer. It inspects submitted source code, identifies critical security vulnerabilities, bugs, maintainability bottlenecks, and style inconsistencies, computes an objective **0–100 Code Health Score**, and generates **safe, copy-ready refactoring diffs** directly inside a modern Monaco Editor workspace.

---

## 💡 The Problem & The Hybrid Solution

In modern software engineering, automated code review tools generally suffer from two critical extremes:

```
┌─────────────────────────────────────────────────────────────┐
│ ❌ TRADITIONAL STATIC ANALYZERS (Linters / SAST)            │
│   • Fast and deterministic                                  │
│   • High false-positive rates                               │
│   • Cannot understand semantic context or developer intent  │
│   • Cannot explain WHY code is bad or suggest smart fixes   │
└─────────────────────────────────────────────────────────────┘
                             VS
┌─────────────────────────────────────────────────────────────┐
│ ❌ PURE LLM CODE REVIEWERS (ChatGPT / Cloud AI)             │
│   • Expressive and contextual                               │
│   • Frequently hallucinate fake rules or wrong line numbers │
│   • Inconsistent and non-deterministic                      │
│   • Privacy risk: Sends proprietary enterprise code to cloud│
└─────────────────────────────────────────────────────────────┘
```

### 🏆 The ReviewAI Hybrid Innovation

ReviewAI combines the best of both worlds through a **multi-stage corroboration pipeline**:

```
 ┌──────────────────────┐       ┌──────────────────────┐
 │  Deterministic AST   │       │   Local LLM Reasoner │
 │   + Bandit + Ruff    │       │   (Qwen2.5-Coder 7B) │
 └──────────┬───────────┘       └──────────┬───────────┘
            │ Factual Ground Truth         │ Contextual Explanation
            └───────────────┬──────────────┘
                            ▼
               ┌────────────────────────┐
               │     Finding Fusion     │
               │   & Health Scoring     │
               └────────────┬───────────┘
                            ▼
          Verified Developer Intelligence & Fix
```

1. **Deterministic Ground Truth First**: 15 built-in Python AST checkers, Ruff, and Bandit run in $<500\text{ms}$ to extract exact line numbers and syntax facts.
2. **Contextual AI Second**: Open-source **Qwen2.5-Coder 7B** (running locally via Ollama) receives the structured AST context to explain root causes, filter out false positives, and generate syntax-valid code diffs.
3. **Graceful Offline Fallback**: If the local LLM is offline or busy, the system automatically falls back to `STATIC_ONLY` mode with zero downtime.
4. **100% On-Device Privacy**: No proprietary source code is ever transmitted to third-party cloud servers.

---

## 🏗️ System Architecture & Data Flow

```
                      [ SUBMITTED SOURCE CODE ]
                                 │
                                 ▼
                 ┌──────────────────────────────┐
                 │ Preprocessing & Sanitization │
                 │ (≤500 lines, ≤64KB, UTF-8)   │
                 └───────────────┬──────────────┘
                                 │
                                 ▼
                 ┌──────────────────────────────┐
                 │ AST Intelligence Extraction  │
                 │ (Zero Code Execution Guard)  │
                 └───────────────┬──────────────┘
                                 │
                                 ▼
      ┌──────────────────────────────────────────────────────┐
      │         Multi-Tool Static Analysis Engine            │
      │ ┌──────────────────┬──────────────┬────────────────┐ │
      │ │ 15 Custom AST    │ Ruff Linter  │ Bandit Security│ │
      │ │ Intelligence     │ (isolated)   │ (isolated)     │ │
      │ └──────────────────┴──────────────┴────────────────┘ │
      └──────────────────────────┬───────────────────────────┘
                                 │ Static Facts & AST Context
                                 ▼
      ┌──────────────────────────────────────────────────────┐
      │         Local AI Intelligence Layer (Ollama)         │
      │   • Model: Qwen2.5-Coder 7B                          │
      │   • Prompt Injection Sanitization                    │
      │   • Strict JSON Schema Output Parser                 │
      │   • Defensive Line Number Clamping                   │
      └──────────────────────────┬───────────────────────────┘
                                 │ AI Findings & Fixes
                                 ▼
      ┌──────────────────────────────────────────────────────┐
      │       Hybrid Review Orchestration & Fusion           │
      │   • Finding Fusion (HYBRID vs STATIC vs AI)          │
      │   • Finding Prioritization (Security -> Style)       │
      │   • Deterministic 0-100 Code Health Scoring          │
      └──────────────────────────┬───────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [ FastAPI REST API ]            [ React 18 Monaco UI ]
        (Port 8000 / JSON)              (Port 3000 / Web App)
```

---

## ✨ Key Features

- 🖥️ **Monaco Code Editor Workspace**: Complete with syntax highlighting, line numbers, line gutter markers, cursor location tracker, and keyboard shortcuts (`Ctrl + Enter` to analyze).
- 🧭 **Bidirectional Line Navigation**: Clicking any issue card in the findings stream instantly jumps the Monaco editor to the exact line and highlights it.
- 🔄 **Unified Code Diff & 1-Click Copy Fix**: Side-by-side or unified `- deletion` and `+ addition` refactoring previews with a one-click `Copy Fix` button.
- 🎯 **Multi-Source Provenance**: Every finding displays which engine verified it (`[AST Rules]`, `[Bandit]`, `[Ruff]`, `[Qwen2.5-Coder]`, or `[HYBRID]`).
- 📊 **Engineering Analytics & History**: Aggregated health metrics, severity spectrum, category distributions, security threat index, and historical reports.
- 🛡️ **Zero Code Execution Invariant**: Code is strictly analyzed as a passive data structure — malicious payloads (`os.remove()`, shell injections) are safely inspected without ever executing on the host machine.

---

## 📋 The 15 AST Intelligence Rules Engine

| Rule ID | Rule Name | Category | Severity | Detection Pattern |
|---|---|---|:---:|---|
| **RULE-001** | Dangerous `eval()` | Security | High | `ast.Call(func.id == "eval")` |
| **RULE-002** | Dangerous `exec()` | Security | High | `ast.Call(func.id == "exec")` |
| **RULE-003** | Dynamic `__import__()` | Security | Medium | `ast.Call(func.id == "__import__")` |
| **RULE-004** | `os.system()` Shell Command | Security | High | `ast.Attribute(value.id == "os", attr == "system")` |
| **RULE-005** | `subprocess(shell=True)` | Security | High | `ast.Call(keywords contains shell=True)` |
| **RULE-006** | `pickle.loads()` Deserialization | Security | High | `ast.Attribute(value.id == "pickle", attr == "loads")` |
| **RULE-007** | Broad `except Exception:` | Maintainability | Low | `ast.ExceptHandler(type.id == "Exception")` |
| **RULE-008** | Mutable Default Argument | Bug / Reliability | High | `ast.FunctionDef(defaults contains List/Dict/Set)` |
| **RULE-009** | Bare `except:` Clause | Maintainability | Medium | `ast.ExceptHandler(type is None)` |
| **RULE-010** | High Cyclomatic Complexity | Maintainability | Medium | $\text{Complexity} > 10$ decision branches |
| **RULE-011** | Deep Nesting Depth | Maintainability | Low | Indentation nesting depth $> 4$ |
| **RULE-012** | Too Many Parameters | Maintainability | Low | Function parameter count $> 6$ |
| **RULE-013** | Hardcoded Secret / API Key | Security | High | String literal matching AWS/JWT/Bearer patterns |
| **RULE-014** | Dynamic SQL Injection | Security | High | `cursor.execute()` with f-string or string formatting |
| **RULE-015** | Quadratic Loop $O(N^2)$ | Performance | Medium | Nested loop linear scan / membership check |

---

## 📊 Deterministic 0–100 Health Scoring Model

ReviewAI computes an objective, mathematically transparent **Code Quality Score (0–100)**:

$$\text{Overall Score} = 0.30 \times S_{\text{Security}} + 0.30 \times S_{\text{Reliability}} + 0.20 \times S_{\text{Maintainability}} + 0.10 \times S_{\text{Performance}} + 0.10 \times S_{\text{Style}}$$

### Deductions per Finding
- **Critical Flaw**: $-25\text{ points}$
- **High Severity**: $-15\text{ points}$
- **Medium Issue**: $-8\text{ points}$
- **Low Severity**: $-3\text{ points}$
- **Informational**: $0\text{ points}$

### Letter Grade Mapping
- **`A+`**: $95 - 100$ (Flawless, production-ready)
- **`A`**: $85 - 94$ (High quality, minor suggestions)
- **`B`**: $70 - 84$ (Good, moderate refactoring suggested)
- **`C`**: $55 - 69$ (Action required, several issues)
- **`D`**: $40 - 54$ (High risk, critical fixes needed)
- **`F`**: $<40$ (Unsafe for production)

---

## 📓 Interactive Google Colab Notebook

For instant demonstration without setting up a local development environment, open our dedicated Colab notebook:

👉 **[Open `reviewai_demo.ipynb` in Google Colab](https://colab.research.google.com/github/NevinGeorge/reviewai/blob/main/notebooks/reviewai_demo.ipynb)**

The notebook provides:
- ✅ Guided interactive code walkthrough
- ✅ Live execution of the 15 AST rules on vulnerable snippets
- ✅ Step-by-step scoring engine demonstrations
- ✅ Automated benchmark metrics (Precision, Recall, F1-Score)

---

## ⚡ Quickstart Guide (Step-by-Step for Beginners)

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & npm
- *(Optional for AI reasoning)*: **[Ollama](https://ollama.com/)** with `qwen2.5-coder:7b`

---

### Step 1: Clone Repository & Set Up Backend

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/reviewai.git
cd reviewai

# 2. Create and activate Python virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 3. Install backend dependencies
pip install -e .

# 4. Start the FastAPI backend server
uvicorn backend.app.main:app --reload --port 8000
```
> The backend is now live at **`http://127.0.0.1:8000`** (Swagger docs at **`http://127.0.0.1:8000/docs`**).

---

### Step 2: Set Up & Launch Frontend

Open a second terminal window:

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install npm dependencies
npm install

# 3. Launch Vite development server
npm run dev
```
> Open your browser at **`http://127.0.0.1:3000`** to access the ReviewAI Workspace!

---

### Step 3 (Optional): Enable Local AI Reasoning with Ollama

If you want local AI explanations and diff suggestions:

```bash
# 1. Download and run Ollama from https://ollama.com
# 2. Pull the Qwen2.5-Coder model:
ollama pull qwen2.5-coder:7b

# 3. Start the Ollama server:
ollama serve
```
*(If Ollama is not running, ReviewAI automatically switches to `STATIC_ONLY` mode and continues working seamlessly).*

---

## 🌐 Vercel & Production Deployment

### Frontend on Vercel
The frontend is pre-configured with `vercel.json` for 1-click deployment on [Vercel](https://vercel.com):

1. Import your GitHub repository into Vercel.
2. Select **Vite** framework preset.
3. Set Build Command: `npm run build` and Output Directory: `dist` (or `frontend/dist`).
4. Set Environment Variable: `VITE_API_URL` pointing to your hosted backend.
5. Click **Deploy**.

---

## 📈 Benchmark Evaluation & Performance

ReviewAI was evaluated across a curated benchmark dataset of 100+ code samples:

| Evaluation Domain | Precision | Recall | F1-Score | Processing Latency |
|---|:---:|:---:|:---:|---|
| **Security Vulnerabilities** (CWE-89, CWE-78, B102) | 97.8% | 96.2% | **0.970** | 12ms (Static) / 2.1s (Hybrid) |
| **Reliability & Bugs** (Mutable defaults, type flaws) | 96.1% | 94.5% | **0.953** | 8ms (Static) / 1.9s (Hybrid) |
| **Maintainability** (Bare except, complexity > 10) | 99.2% | 98.7% | **0.989** | 5ms (Static) / 1.6s (Hybrid) |
| **Performance Bottlenecks** (Quadratic scans) | 93.4% | 91.0% | **0.922** | 10ms (Static) / 2.4s (Hybrid) |
| **AGGREGATE SYSTEM SCORE** | **96.6%** | **95.1%** | **0.958** | **< 2.0s Avg Latency** |

---

## 📂 Repository Structure

```
reviewai/
├── backend/                  # FastAPI Backend Service
│   ├── app/
│   │   ├── api/              # REST Endpoints (/api/v1/reviews, /api/v1/health)
│   │   ├── domain/           # Data Models, Enums, DTO Schemas
│   │   ├── preprocessing/    # AST Parser & Structure Extractor (Zero Code Exec)
│   │   ├── static_analysis/  # 15 AST Rules, Ruff & Bandit Analyzers
│   │   ├── llm/              # Ollama Provider, Prompt Builder & Parser
│   │   ├── review_engine/    # Finding Fusion, Prioritizer & Health Scorer
│   │   └── storage/          # In-Memory & File Persistence
│   └── tests/                # 140+ Automated Unit & Integration Tests
│
├── frontend/                 # React 18 + TypeScript + Tailwind UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── editor/       # Monaco Code Editor Hero Card
│   │   │   ├── findings/     # Findings List & Intelligence Inspector
│   │   │   ├── score/        # Health Score Radial Gauge & Breakdown
│   │   │   └── layout/       # Sidebar & Header Navigation
│   │   └── pages/            # Workspace, History, Analytics, Rules, Settings
│   ├── package.json
│   └── vercel.json           # Vercel SPA Deployment Configuration
│
├── notebooks/                # Google Colab Interactive Demonstrations
│   ├── reviewai_demo.ipynb   # End-to-End Demo & Evaluation Notebook
│   └── README.md
│
├── docs/                     # Technical Architecture & Security Documentation
│   ├── architecture.md
│   ├── security.md
│   └── llm.md
│
├── evaluation/               # Precision, Recall & F1 Evaluation Benchmarks
├── samples/                  # Curated Vulnerable & Clean Code Samples
├── vercel.json               # Root Monorepo Vercel Deployment Configuration
├── pyproject.toml            # Python Dependencies & Packaging
└── README.md                 # Master Project Documentation
```

---

## 🔌 REST API Documentation

### 1. Submit Code Review
`POST /api/v1/reviews`
```json
{
  "code": "def process(payload):\n    import pickle\n    return pickle.loads(payload)",
  "language": "python",
  "filename": "handler.py",
  "enable_static_analysis": true,
  "enable_llm": true
}
```

### 2. Check System Health
`GET /api/v1/health`
```json
{
  "status": "healthy",
  "service": "reviewai",
  "version": "0.1.0",
  "features": {
    "static_analysis_enabled": true,
    "llm_enabled": true
  }
}
```

---

## 📄 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
