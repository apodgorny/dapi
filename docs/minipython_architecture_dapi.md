
# MiniPython Interpreter in DAPI

This document provides an in-depth explanation of how the MiniPython interpreter works in the DAPI architecture. It describes its purpose, structure, evaluation mechanism, operator delegation, error tracing, and its role in the agentic execution environment.

---

## 1. Purpose of MiniPython

MiniPython is a custom interpreter designed to evaluate a safe subset of Python AST nodes dynamically. It enables structured, recursive logic to be expressed and executed at runtime without risking the security or unpredictability of full Python execution.

---

## 2. Core Features

- Executes AST-based MiniPython code.
- Accepts a list of operators and dynamically resolves them.
- Uses a strict environment stack (`env_stack`) for variables.
- Supports async evaluation (`await` propagation).
- Interfaces with other interpreters via a callback (`call_operator_callback`).
- Maintains detailed execution trace through `ExecutionContext`.

---

## 3. Initialization

```python
MiniPython(
    operators: list[dict],
    operator_callback: Callable[[str, dict], Awaitable[dict]],
    context: Optional[ExecutionContext] = None
)
```

- Parses operators into `self.functions` based on AST.
- Injects built-ins and environment types.
- Tracks recursive state via `_was_called` and `_root_operator_name`.

---

## 4. Evaluation Flow

### 4.1 Entry Point

```python
await minipy.call_main(operator_name, input_dict)
```

- Initializes env with `input`.
- Pushes to `env_stack`.
- Calls `eval(root_function_node)`.

### 4.2 Recursive `eval(node)`

- Uses `match`-based dispatch on AST node types.
- Evaluates constructs like `Return`, `If`, `Call`, `BinOp`, etc.
- Each `eval(...)` pushes `(operator, lineno)` into context.
- Always pops on exit (in `finally`).

---

## 5. Operator Delegation

If a `Call` is not to a known MiniPython function:

- It's assumed to be a call to another operator.
- Delegated via:

```python
await self.operator_callback(name, input_dict)
```

- The callback is resolved by the surrounding interpreter (usually `PythonInterpreter`).

---

## 6. Environment Stack (`env_stack`)

- Each scope is a `dict` of variable names to values.
- Supports nested evaluation contexts.
- Stack-like behavior: push on `call_main`, pop on exit.

---

## 7. ExecutionContext Integration

- All evaluation steps are traced:

```python
context.push(operator, line, <interpreter_name>)
...
context.pop()
```

- On error, `MiniPythonRuntimeError` includes the stack:

```python
MiniPythonRuntimeError(
    msg=str(e),
    operator=current_operator,
    line=current_line,
    stack=context.stack
)
```

- Enables precise tracebacks with:

```
  in main @ line 1
  in brancher @ line 2
```

---

## 8. Error Handling

- Catches any exception, enriches with `operator`, `line`, and `context`.
- Transforms into `MiniPythonRuntimeError`.
- Can be consumed and rethrown by `DapiException.consume()`.

---

## 9. Design Goals

- Predictability: clear and safe subset of Python
- Traceability: errors with structured context
- Composability: interoperability with Plugin and LLM operators
- Isolation: no mutation of global Python state

---

## 10. Summary

MiniPython is a lightweight, deterministic, introspectable execution engine built for agentic composition. It enables runtime logic that is:

- Expressive yet secure
- Dynamic yet controlled
- Fully traceable across calls and interpreters

It is the foundation for procedural logic in the DAPI system.

---
