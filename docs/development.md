# ReviewAI — Development & Contributing Guide

## 1. Prerequisites

- **Python**: Version `3.11` or higher
- **Node.js**: Version `18.0` or higher (for frontend development)
- **Ollama**: (Optional for local LLM reasoning; Mock provider & Static-Only fallback available) [ollama.com](https://ollama.com)
  - Recommended model: `ollama pull qwen2.5-coder:7b-instruct`
- **Ruff & Bandit**: (Optional CLI static analysis tools; built-in AST rules available)
- **Docker**: (Optional for containerized deployment)

---

## 2. Environment Setup

### Step 1: Clone and Configure Environment

```bash
# Clone the repository
git clone <repository_url> review-ai
cd review-ai

# Copy environment template
cp .env.example .env
```

### Step 2: Set Up Backend Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install backend package with development and analysis dependencies
pip install -e ".[dev,analysis,evaluation]"
```

---

## 3. Running the Backend API Server

Start the local development server with auto-reload:

```bash
# Start FastAPI backend server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Interactive API Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 4. Running Verification & Unit Tests

Verify the backend foundation, AST engine, static analysis suite, LLM layer, review engine, and run all unit tests:

```bash
# Run comprehensive engine self-checks (Modules 1 through 6)
python scripts/check_foundation.py

# Run complete pytest test suite
pytest backend/tests -v
```

---

## 5. Development Roadmap Progress

- **[x] MODULE 1**: Foundation & Architecture
- **[x] MODULE 2**: Backend & API Foundation
- **[x] MODULE 3**: Code Preprocessing & AST Engine
- **[x] MODULE 4**: Hybrid Static Analysis & Evidence Engine
- **[x] MODULE 5**: Local LLM Intelligence Layer
- **[x] MODULE 6**: Hybrid Review Engine & Quality Scoring (Current)
- **[ ] MODULE 7**: Premium Frontend
- **[ ] MODULE 8**: Evaluation & Testing
- **[ ] MODULE 9**: Docker, Security & Production Hardening
- **[ ] MODULE 10**: Documentation, Demo & Final Submission
