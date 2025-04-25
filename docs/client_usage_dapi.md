
# DAPI Client: Usage and Operator Creation

This document explains how the DAPI client works, with a focus on its role in defining and interacting with LLM and MiniPython operators. It details the request flow, configuration options, and examples of dynamic operator definitions.

---

## 1. Purpose of the Client

The DAPI client is a Python library that interacts with the DAPI backend via HTTP requests. It provides utility functions for:

- Creating and deleting operators
- Invoking operators and viewing results
- Resetting the server state
- Uploading source code for dynamic operators
- Presenting output with color-coded, human-friendly formatting

---

## 2. Basic Usage

### Import
```python
from dapi.lib.client import Client
```

### Invoke an Operator
```python
result = Client.invoke("square", {"x": 3})
```

---

## 3. Creating Operators

### 3.1 MiniPython Operators

These are defined using a subset of Python, parsed to AST.

#### Example
```python
Client.create_operator(
    name        = "times_two",
    input_type  = {"type": "object", "properties": {"x": {"type": "number"}}, "required": ["x"]},
    output_type = {"type": "object", "properties": {"x": {"type": "number"}}, "required": ["x"]},
    code        = """
def times_two(input):
    return {"x": input["x"] * 2}
""",
    interpreter = "python"
)
```

---

### 3.2 LLM Operators

LLM operators are defined by specifying a prompt template that uses placeholders (e.g., `{{input.name}}`). The model fills in the template at runtime.

#### Example
```python
Client.create_operator(
    name        = "greet_user",
    input_type  = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    output_type = {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
    code        = "Hello, {{input.name}}! Welcome to DAPI.",
    interpreter = "llm",
    config      = {"model_id": "ollama::gemma3:4b", "temperature": 0.7}
)
```

---

## 4. Configuration Options

### General
- `interpreter`: `python` | `llm` | `plugin`
- `code`: string (MiniPython or prompt text)
- `config`: additional settings (model id, temperature, etc. for LLMs)

### LLM-specific
- `model_id`: model to use, e.g., `ollama::gemma3:4b`
- `temperature`: sampling randomness
- `system`: optional system prompt

---

## 5. Client-Side Compilation

You can compile a Python file with multiple operators and upload them all:

```python
Client.compile("path/to/operators.py")
```

This extracts the operators and calls `create_operator()` on each.

---

## 6. Error Reporting

- Errors from the server are caught and colored based on severity.
- `halt`, `beware`, `fyi` levels are supported.
- Stack traces are shown for `MiniPythonRuntimeError`.

---

## 7. Summary

The client is your portal into DAPI’s compositional operator world. It lets you:
- Define operators dynamically
- Switch between LLM, MiniPython, and Plugin styles
- Maintain human-readable control over execution and diagnostics

It’s a universal command wand for your agentic logic.

---
