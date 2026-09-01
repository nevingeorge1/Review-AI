# ReviewAI — Security & Privacy Architecture

## 1. Core Security Guarantees

ReviewAI is engineered under the principle of **Zero-Trust Input & Privacy by Default**.

---

## 2. Prohibition of Arbitrary Code Execution

> [!CAUTION]
> **Fundamental Security Invariant**: ReviewAI is exclusively a static analysis and LLM reasoning engine. ReviewAI **NEVER** executes, evaluates, imports, or runs user-submitted source code in any runtime environment (no `exec()`, `eval()`, or dynamic imports).

- All syntactic checks are performed via Abstract Syntax Tree (AST) parsing (`ast.parse()` in safe mode).
- Linters and security scanners inspect code as raw text streams or AST nodes without invoking code entry points.

---

## 3. Input Validation & Denial-of-Service (DoS) Protection

To prevent resource exhaustion and buffer exploitation:

1. **Maximum Source Lines**: Default limit of `500` lines (configurable via `MAX_SOURCE_LINES`). Submissions exceeding this limit are rejected at the API boundary with a `413 Payload Too Large` equivalent (`SOURCE_TOO_LARGE`).
2. **Maximum Payload Size**: Default limit of `65,536` bytes / 64 KB (configurable via `MAX_SOURCE_SIZE`).
3. **Payload Sanitization**: Null-byte injection checks, binary content rejection, and strict UTF-8 encoding verification.

---

## 4. Privacy & Data Handling Guarantees

1. **Local-First Processing**: In standard configuration, all code analysis and LLM reasoning occur locally on the host machine via Ollama. Source code is never transmitted to external third-party servers.
2. **Safe Logging Policy**: 
   - Complete source code submissions are **NEVER** written to application logs.
   - Logs only record metadata: `submission_id`, `language`, `line_count`, `byte_size`, `finding_count`, and `duration_ms`.
3. **No Secret Retention**: Ephemeral in-memory handling by default. No persistent storage of raw code without explicit user consent.
4. **Environment Isolation**: No hardcoded API keys or credentials. Secrets and environment configurations are managed strictly via environment variables loaded through `.env`.

---

## 5. Safe Temporary File Handling

When external static analysis tools require temporary file paths:
- Temporary files are created in isolated OS temp directories with restricted read/write permissions (`0600`).
- Files are cleaned up immediately in deterministic `finally` blocks.
- Random UUID-based filenames prevent symlink and directory traversal attacks.

---

## 6. Error Handling & Information Disclosure

- Internal stack traces, raw system paths, and infrastructure details are stripped from client-facing API responses.
- Standard machine-readable error codes (e.g., `PARSER_FAILURE`, `SYNTAX_ERROR`, `LLM_TIMEOUT`) are returned with sanitized messages.
- Request correlation IDs (`X-Request-ID`) allow internal tracing without revealing internal state to callers.
