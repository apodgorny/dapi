# DAPI Modification Log (April 2025)

This document tracks the architectural simplification and restructuring of DAPI as of April 2025. It outlines the key conceptual shifts, completed refactors, and upcoming implementation steps.

---

## 🔄 Key Changes in Philosophy

### 1. **Operators as Classes**
Operators are no longer abstract functions or scripts — they are now fully defined Python classes with typed input/output models (`InputType`, `OutputType`) and an `invoke()` method. This formalization provides:
- Better introspection and validation via Pydantic
- Easier persistence (classes are stored as-is)
- Native support for documentation (via class docstrings)

Each operator is now a **serializable, executable, and self-descriptive unit**, which can be sent across API boundaries and reloaded for execution.

### 2. **Interpreter Types Simplified**
Instead of having ambiguous interpreter types (`plugin`, `python`, etc.), DAPI now uses three canonical categories:
- **`full`** – Executes full Python classes authored by humans using standard Python semantics
- **`mini`** – Executes simplified, safe Python-like AST evaluated dynamically (used for AI-defined logic)
- **`llm`** – Executes natural language prompts interpreted by large language models (LLMs)

This distinction ensures a clear boundary between static, dynamic, and generative execution models.

### 3. **ExecutionContext as Universal Spine**
DAPI now uses `ExecutionContext` to track the logical execution stack across all interpreters:
- Every operator call is traced
- Errors carry a full stack with line numbers and interpreter source
- Nested operator calls are fully introspectable

This is key to human-readable diagnostics and ensures that composed logic remains debuggable and explainable.

### 4. **Unified External Operator Invocation**
In earlier versions, each interpreter had its own way of calling other operators (e.g. injected `call` functions in `plugin` mode). Now, every interpreter delegates unknown calls to a single method:

```python
await operator_service.call_external_operator(name, input, context)
```

This unifies control flow and reduces interpreter complexity — they no longer need internal registries or injection logic. It also standardizes error handling and traceability.

### 5. **Everything is an Operator**
There is no longer a separate concept of "instance" or "runtime wrapper." All execution is the invocation of an operator class with data. This moves DAPI toward a **functional model of execution**, where operators are reusable, stateless, and composable.

---

## ✅ What Has Been Done

### 🔹 OperatorService
- Removed plugin function wrapping and dynamic callable injection
- Added `call_external_operator()` as a unified gateway to call any operator
- Updated `register_plugin_operators()` to store full class code and use interpreter=`full`
- Updated `invoke()` to delegate to the correct interpreter based on type

### 🔹 Client & Compiler
- `Code.serialize()` now stores full class source, preserving original structure
- `Client.compile()` sends operator classes unchanged to the server

### 🔹 Interpreter Contracts
- All interpreters now:
  - Accept `ExecutionContext`
  - Use `context.push(...)` and `context.pop()`
  - Delegate unknown names via `call_external_operator`

### 🔹 FullPythonInterpreter
- Legacy magic-injection and context wrapping removed
- Will use `FullPython(...)` engine to interpret full class files with external operator delegation

### 🔹 MiniPythonInterpreter
- Already supported external delegation via `operator_callback`
- Will converge in architecture with `FullPythonInterpreter`

---

## 🛠️ Planned Work

### 🔜 FullPython Engine
- Create `FullPython` interpreter that:
  - Executes full class code via `exec()` or import
  - Uses AST or scope introspection to detect unresolved calls
  - Delegates to `call_external_operator` when needed
  - Wraps stack with context tracking and exception catching

### 🔜 Base Interpreter Abstraction
- Extract shared methods like `ensure_context()`, `trace()`, and `call_external_operator()`
- Move to `Interpreter` base class

### 🔜 Remove OperatorInstanceRecord
- Remove all instance tracking logic (schemas, DB, service)
- Execution is now a pure function call, not a persistent entity

### 🔜 CLI and Server Alignment
- Ensure `dapi/process.py` and server `invoke()` interface are symmetrical
- Client should not transform any code — only upload and invoke

### 🔜 LLM Interpreter Enhancements
- Allow LLMs to delegate to other operators via inline syntax (`{{call(...)}}`)
- Inject trace metadata into prompt headers (e.g. depth, stack)

---

## 💡 Guiding Principle

> **Everything is an operator. Execution is a conversation between interpreters.**

The new DAPI favors simplicity, composability, and traceability. All execution flows through shared context. The only abstraction is `Operator`, and the only responsibility of interpreters is to run it safely, visibly, and interoperably.
