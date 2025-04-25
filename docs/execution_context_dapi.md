
# Execution Context in DAPI

This document explains how execution context works across the three types of interpreters in DAPI, and how it integrates with the three types of operators: MiniPython, Plugin (FullPython), and LLM. It also explores how this context enables structured togetherplay between dynamic code, deterministic Python logic, and language model interactions.

---

## 1. Overview of Execution Context

The `ExecutionContext` is a runtime structure that tracks the path of operator execution. It is essentially a stack that collects entries in the form of `(operator_name, line_number)`. Each interpreter contributes to this context as execution proceeds.

This context is used to:

- Provide detailed and clean stack traces for debugging.
- Preserve trace across nested and recursive operator calls.
- Maintain introspectable context across multiple interpreters.

---

## 2. Interpreters

### 2.1 MiniPythonInterpreter

**Purpose**: Executes safe subset of Python AST with dynamic evaluation.

- Receives the `ExecutionContext` via `context` parameter.
- Every `eval(node)` pushes `(operator, line)` into the context.
- Ensures `context.pop()` is called in `finally` to maintain stack correctness.
- On error, raises `MiniPythonRuntimeError` that includes context stack.
- Delegates unknown calls to other operators via `call_operator_callback`.

### 2.2 PluginInterpreter (FullPython)

**Purpose**: Executes static Python classes extending `Operator` with a predefined `invoke()` method.

- Invokes external logic written by developers.
- Wraps plugin `invoke()` with `context.push()` and `context.pop()`.
- Accepts `ExecutionContext` as argument.
- Ensures the trace is preserved when MiniPython calls out to Plugin-based logic.

### 2.3 LLMInterpreter

**Purpose**: Executes prompt-based logic using models like `ollama::gemma3:4b`.

- Replaces `{{input.x}}` placeholders with actual values.
- Uses context to track the invocation as a logical operator.
- Pushes `(operator, 1)` into context to mark prompt as line 1.
- Allows LLM steps to integrate into unified stack trace.

---

## 3. Operator Types

### 3.1 MiniPython Operators

- Defined by code written in a safe Python-like syntax.
- Stored as AST and interpreted.
- Ideal for flexible, dynamic behaviors and embedded logic.

### 3.2 Plugin Operators

- Defined by real Python classes on disk.
- Provide deterministic behavior.
- Used for precision or performance-critical operations.

### 3.3 LLM Operators

- Prompt-based, generative.
- Used for creative, open-ended tasks.
- Can conform to strict schemas via output validation.

---

## 4. Togetherplay — Interoperability Model

The DAPI system supports composition across all 3 operator types. The execution context is the bridge that makes them feel like a single space of logic:

- MiniPython can call Plugin or LLM operators through `call()`.
- Plugin code can in turn call other operators via injected `invoke()`.
- LLMs appear in the stack as just another function.
- Traceability and introspection are guaranteed across all types.

This architecture enables the blending of:
- **Flexibility (MiniPython)**
- **Precision (Plugin)**
- **Generativity (LLM)**

...into a single orchestrated flow.

---

## 5. Example Trace

```
HALT: NameError: name 'call' is not defined (operator: brancher, line: 19)
  in brancher @ line 19
  in main     @ line 2
  in main     @ line 1
```

This trace was made possible by each interpreter respecting the context.

---

## 6. Future Extensions

- Add support for richer metadata per frame: file, source type.
- Group repetitive calls for cleaner display.
- Let context trace be used for telemetry or audit logging.
- Allow context injection into LLM prompts.

---

## 7. Summary

`ExecutionContext` provides:
- Cross-interpreter traceability
- Stack-based error introspection
- Unified execution semantics for composed agentic logic

It is the invisible thread that binds static, dynamic, and generative execution into a single DAPI language.

---
