# ReviewAI — Sample Code Fixtures

## Overview

This directory contains curated static Python source code fixtures used for AST intelligence testing, benchmarking, and demonstration.

> [!CAUTION]
> **Safety Invariant**: All code in this directory is treated strictly as **DATA**. No file in this directory is ever imported, executed, or dynamically evaluated.

---

## Sample Fixtures

- [`samples/python/basic.py`](file:///C:/Users/NevinGeorge/Desktop/clay/samples/python/basic.py): Clean, straightforward functions, type annotations, and docstrings.
- [`samples/python/complex.py`](file:///C:/Users/NevinGeorge/Desktop/clay/samples/python/complex.py): Class inheritance, async methods, nested control flow, error handling, and high cyclomatic complexity.
- [`samples/python/incomplete.py`](file:///C:/Users/NevinGeorge/Desktop/clay/samples/python/incomplete.py): Malformed Python snippet with syntax errors for parser resilience testing.
- [`samples/python/security_signals.py`](file:///C:/Users/NevinGeorge/Desktop/clay/samples/python/security_signals.py): Examples of `eval`, `exec`, `os.system`, `subprocess.run`, `pickle.loads`, and `yaml.load` calls for static signal verification.
- [`samples/python/vulnerable_sample.py`](file:///C:/Users/NevinGeorge/Desktop/clay/samples/python/vulnerable_sample.py): Module 1 sample containing hardcoded secrets and mutable default arguments.
- [`samples/python/clean_sample.py`](file:///C:/Users/NevinGeorge/Desktop/clay/samples/python/clean_sample.py): Clean, idiomatic baseline implementation.
