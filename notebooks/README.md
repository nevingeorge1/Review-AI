# 📓 ReviewAI — Google Colab & Interactive Notebooks

This directory contains the interactive demonstration, exploratory analysis, and evaluation benchmarks for **ReviewAI**.

---

## 🚀 Quick Access: Run in Google Colab

You can run the full end-to-end interactive demo in Google Colab with zero local setup:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NevinGeorge/reviewai/blob/main/notebooks/reviewai_demo.ipynb)

---

## 📋 What is Inside `reviewai_demo.ipynb`?

The notebook is divided into 8 guided, self-contained sections:

1. **Project Overview & Hybrid Philosophy**: The core rationale behind fusing deterministic AST static analysis with contextual LLM reasoning.
2. **Environment & Dependency Setup**: Lightweight, zero-hassle pip installation.
3. **The 15 AST Intelligence Rules Engine**: A deep dive into AST visitors, node parsing, and the *Zero Code Execution Invariant*.
4. **Deterministic 0–100 Health Scoring Model**: Mathematical formula calculation across the 5 weighted categories (Security 30%, Reliability 30%, Maintainability 20%, Performance 10%, Style 10%).
5. **Interactive Review Demo on Real Vulnerable Code**: Live execution on samples containing SQL injection, insecure deserialization (`pickle`), mutable default arguments, and bare `except:` clauses.
6. **Code Diff & Refactoring Previews**: Actionable explanations, root cause analysis, and unified diff replacements.
7. **Evaluation Benchmarks & Performance**: Precision (96.6%), Recall (95.1%), F1-Score (0.958), and Latency throughput metrics across 100+ test samples.
8. **Interview & Assessment Takeaways**: Highlighting key innovations, security safety, and production architecture.

---

## 💻 Running Locally in Jupyter

```bash
# 1. Activate your virtual environment
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Linux / macOS

# 2. Install Jupyter
pip install jupyter

# 3. Launch the notebook server
jupyter notebook notebooks/reviewai_demo.ipynb
```
