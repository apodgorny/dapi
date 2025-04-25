
# DAPI Error System and MiniPython Integration

This document details the architecture of error handling in DAPI, how it unifies exceptions into `DapiException`, and how MiniPython participates in and extends this system.

---

## 1. Overview

DAPI uses a centralized error model centered on `DapiException`. All raised errors from services, interpreters, or runtime logic are expected to be:

- caught
- annotated with useful fields (`line`, `file`, `operator`, `error_type`)
- converted into structured JSON errors

This allows the client to uniformly parse, render, and react to errors.

---

## 2. `DapiException`

```python
DapiException(
    status_code = 400,
    detail      = str | dict,  # should include 'detail', 'severity', and optionally 'line', 'file', 'operator', 'error_type'
    severity    = 'halt' | 'beware' | 'fyi'
)
```

- Raised directly in API and services
- Produced via `DapiException.consume(e)` for foreign errors

### `.consume()`
- Converts Python exceptions into `DapiException`
- Recognizes known types (like `ImportError`, `ValidationError`, `MiniPythonRuntimeError`, etc.)
- Extracts useful metadata

---

## 3. `MiniPythonRuntimeError`

```python
MiniPythonRuntimeError(
    msg      = str,
    operator = str,
    line     = int,
    stack    = list[tuple[operator, line]]
)
```

- Raised by MiniPython if any error occurs during `eval(node)`
- All exceptions (even `DapiException`) get caught and wrapped with precise context
- Error is passed through `.consume()` and transformed into a proper `DapiException`

This means that **MiniPython errors appear like any other**, but with:
- `error_type: MiniPythonRuntimeError`
- `stack` attached to the final trace

---

## 4. Client Behavior

The client recognizes all structured errors and formats them:
- Severity-based prefix (`HALT`, `BEWARE`, `FYI`)
- Trace rendering in gray
- Fallback if `.detail` is malformed

### Example:
```
HALT: NameError: name 'call' is not defined (operator: brancher, line: 19)
  in main     @ line 1
  in brancher @ line 2
```

---

## 5. Plugins and LLMs

- PluginInterpreter wraps its `invoke()` in try/except and rethrows `ValueError` → consumed as `DapiException`
- LLMInterpreter uses `.consume()` directly

All interpreters participate in error unification.

---

## 6. Summary

The DAPI error system ensures:
- **Unification**: One exception type with rich metadata
- **Composability**: All interpreters feed into the same stream
- **Traceability**: MiniPython emits structured errors with stack
- **Visibility**: Clients can render all errors meaningfully

Errors are no longer strings—they are structured events.

---
