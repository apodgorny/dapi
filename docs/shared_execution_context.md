
# Shared Execution Context in DAPI

This document describes the architecture and behavior of `ExecutionContext`, a unified tracing mechanism that spans all types of interpreters (MiniPython, Plugin, LLM) in DAPI.

---

## 1. Purpose of ExecutionContext

The `ExecutionContext` class provides a shared call stack that traces the logical flow of operator invocations regardless of the underlying interpreter.

---

## 2. Context Lifecycle

### Initialization
Each interpreter receives or creates an `ExecutionContext`, often with the top-level operator:
```python
context = ExecutionContext(root=operator_name)
```

### During Execution
On every evaluation or invocation:
```python
context.push(operator_name, line_number, <interpreter_name>)
...
context.pop()
```
This happens across:
- MiniPython AST evaluation (`eval`)
- Plugin `invoke()`
- LLM prompt resolution

### On Error
If an error occurs:
- The current stack is captured via `context.stack`
- Passed into `MiniPythonRuntimeError` or `DapiException`
- Final error contains the full trace chain

---

## 3. Composition and Propagation

Interpreters must pass the same context when:
- Delegating to external operators
- Calling `call_operator(name, input)` in MiniPython

This ensures all recursive operator calls build a shared stack:
```
main @ line 1
  → brancher @ line 2
    → brancher_friend @ line 3
```

---

## 4. Runtime Behavior

### MiniPython
- Root interpreter in most chains
- Maintains `env_stack` and context
- Delegates external calls via callback with context

### Plugin Interpreter
- Wraps static class `invoke()`
- Pushes/pops context explicitly

### LLM Interpreter
- Pushes current operator with dummy `line=1`
- Errors are routed via `.consume()` with context trace

---

## 5. Trace Design

The trace is rendered like:
```text
HALT: TypeError: x must be int (operator: brancher, line: 7)
  in main @ line 1
  in brancher @ line 2
```

---

## 6. Design Philosophy

ExecutionContext makes the system:
- **Interpreter-agnostic**: one trace, many languages
- **Error-aware**: always context-rich
- **Chainable**: flows through nested calls
- **Minimal**: uses only `push()` / `pop()`

---

## 7. Summary

ExecutionContext is the invisible spine of DAPI’s execution graph.
It makes multi-interpreter logic traceable, debuggable, and human-readable.
It binds operator calls across boundaries into one intelligible narrative.

---
