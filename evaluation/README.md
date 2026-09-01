# ReviewAI — Evaluation Framework Specification

## 1. Overview

The evaluation framework provides quantitative validation of ReviewAI's review quality, speed, and reliability. It will be implemented in **Module 8**.

---

## 2. Target Metrics

| Metric | Target | Formula / Description |
| :--- | :---: | :--- |
| **Precision** | > 85% | $TP / (TP + FP)$ — Ratio of genuine issues identified to total reported |
| **Recall** | > 80% | $TP / (TP + FN)$ — Ratio of identified ground-truth issues to total existing issues |
| **F1-Score** | > 82% | Harmonic mean of Precision and Recall |
| **Latency (Static Analysis)** | < 150ms | AST + Ruff + Bandit total execution time |
| **Latency (Full Hybrid Review)** | < 3.5s | End-to-end review latency with local Qwen2.5-Coder model |
| **Throughput** | > 20 req/min | Maximum sustained review throughput |

---

## 3. Directory Layout

- `datasets/`: Curated benchmark code snippets with labeled ground-truth bugs, security flaws, and style violations.
- `metrics/`: Python evaluation scripts calculating precision, recall, F1, and confusion matrices.
- `benchmarks/`: Automated load testing and latency measurement scripts.
- `results/`: Output logs, CSVs, and visualization plots generated from benchmark runs.
