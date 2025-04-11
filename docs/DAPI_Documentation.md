# Dynamic API (DAPI) — Complete Specification

*Version: April 2025*

---

## 1. Vision & Principles

DAPI empowers runtime‑evolving systems by unifying code and data under a single reflective model.

> **DAPI = live language + unified operator‑transaction model.**> Вся логика и данные описываются самими данными, исполняются в рантайме и могут рефакториться «изнутри».

- **Self‑reflective & self‑extensible** — любой уровень DAPI (типы, операторы, транзакции, даже мета‑операции) доступен как обычный оператор.
- **Minimal instruction set** — система держится на ~10 базовых операторов, обеспечивающих Turing‑полноту и рефлексию.
- **Uniform data plane** — JSON Schema для типов, Pydantic для валидации, FastAPI + OpenAPI 3.1 для внешнего контракта.
- **Human‑AI collaboration** — LLM‑интерпретатор («llm») встроен на равных с `python` и `node`.
- **Garbage‑free by design** — транзакции удаляются после `invoke`; композиты очищают внутренние цепочки.

---

## 2. Core Concepts

| Term            | Role                                                                |
| --------------- | ------------------------------------------------------------------- |
| **Type**        | JSON Schema; регистрируется оператором `create_type`.               |
| **Operator**    | Абстрактный исполняемый блок. 3 видов: `atomic_static`,             |
|                 | `atomic_dynamic`, `composite`.                                      |
| **Transaction** | Инстанс вызова оператора; живёт до `invoke_transaction`.            |
| **Assignment**  | Направленное копирование данных `from` → `to` (input/scope/output). |
| **Scope**       | Общий контекст для цепочек; создаётся `create_scope`.               |

---

## 3. Minimal Instruction Set

| Category | Operator & Signature | Purpose |
|----------|---------------------|---------|
| **Type** | `create_type(name, json_schema)` → *type_name* | Register a JSON Schema under a unique name |
| **Operator** | `create_operator(name, input_type, output_type, code, interpreter)` → *operator_name* | Define an executable unit (static, dynamic or composite) |
| **Transaction** | `create_transaction(operator)` → *tx_id* | Instantiate a single invocation of an operator |
| **Assignment** | `create_transaction_assignment(tx_id, from, to)` → *assign_id* | Map a value or accessor into the transaction `input` |
| **Composite** | `create_scope(name, tx_ids, interpreter, scope)` → *operator_name* | Wrap several transactions into a reusable composite operator |
| **Invocation** | `invoke_transaction(tx_id)` → *output* | Execute the transaction and auto‑delete it |
| **Introspection** | `list_types()` → *list[type_name]* | Enumerate registered types |
| **Introspection** | `list_operators()` → *list[operator_name]* | Enumerate registered operators |
| **Introspection** | `list_transactions()` → *list[tx_id]* | Enumerate existing transactions |
| **Deletion** | `delete_type(name)` → *status* | Remove a type by name |
| **Deletion** | `delete_operator(name)` → *status* | Remove an operator by name |
| **Deletion** | `delete_transaction(tx_id)` → *status* | Remove a transaction before invocation |

> **Note**  Higher‑level behaviours (loops, branches, LLM helpers) are expressed by composing the primitives above.

## 4. Execution Semantics

The life‑cycle of any computation in DAPI follows four deterministic steps:

1. Создаём транзакцию под оператор.
2. Наполняем `input` через `create_transaction_assignment`.
3. `invoke_transaction` — выполняет код, возвращает `output`, удаляет мусор.
4. Composite‑оператор выполняет внутреннюю цепочку и тоже очищается.

---

## 5. Interpreters

| Name     | Runtime                                | When to choose |
|----------|----------------------------------------|----------------|
| `python` | Embedded `exec` in a sandboxed scope   | Quick deterministic logic, data wrangling, glue code |
| `node`   | External Node/Deno subprocess          | Existing JS/TS libraries, async I/O heavy tasks |
| `llm`    | Call to an LLM provider (Ollama, OpenAI) | Generative or fuzzy logic, natural‑language transforms |

Интерпретаторы сканируются из папки `interpreters/` при запуске и регистрируются в `InterpreterRegistry`; в Pydantic‑схемах используется динамический `InterpreterEnum`.

---

## 6. Current Code Structure

```
app/
 ├─ dapi_controller.py        # FastAPI routes + runtime define()
 ├─ dapi_schemas.py           # All *Input / *Output Pydantic models
 ├─ services/
 │    ├─ TypeService.py       # CRUD for JSON Schema types
 │    ├─ OperatorService.py   # Runtime registration & persistence of operators
 │    └─ TransactionService.py# Create / invoke / delete transactions
 ├─ interpreters/             # python/, node/, llm/ — scanned on startup
 │    ├─ python/
 │    ├─ node/
 │    └─ llm/
 └─ tests/
      ├─ unit/
      └─ integration/
```

### 6.1 dapi_schemas.py

- `InterpreterEnum` — жёстко `python|llm`, плюс закомментированная динамика.
- Симметричные схемы `CreateTypeInputSchema` / `TypeInfoSchema` и т.д.

### 6.2 dapi_controller.py

- Все статические эндпоинты используют строгие схемы.
- `define()` позволяет регистрировать runtime‑операторы.

---

## 7. FastAPI Layer

- **Router prefix** `/dapi`.
- Статические эндпоинты (`create_type`, …) используют строгое разделение `*InputSchema` ↔ `*Info/List*OutputSchema`.
- Динамические эндпоинты создаются функцией `define()`:

```python
async def handler(input: InputModel) -> OutputModel: ...

define('double', InputModel, OutputModel, handler, description='Doubles value')
```

`define()` оборачивает хэндлер в FastAPI route с валидацией входа/выхода.

---

## 8. Testing Strategy

| Level | Focus | Tools |
|-------|-------|-------|
| **Unit** | Pydantic validation of every *Input / Output* schema | `pytest`, `pydantic`’s `validate_call` |
| **Integration** | FastAPI routes with in‑memory services | `fastapi.testclient` |
| **Contract** | Generated OpenAPI ⇄ stored JSON Schema snapshots | `schemathesis`, `pytest‑snapshot` |
| **Fractional Build‑Up** | Types → Operators → Transactions → Composite → Dynamic | CI matrix stages |

> *Tip:* Run `pytest -m schema` to isolate pure‑schema tests for rapid iteration.

---

## 9. Road‑Map

| Stage | Milestone | Status |
|-------|-----------|--------|
| **🌱 Q2 2025** | Dynamic `InterpreterEnum` via `InterpreterRegistry` | 🟡 In Progress |
| **♻️ Q2 2025** | `OperatorService.save_operator` автогенерирует FastAPI‑роут | 🔜 |
| **🧹 Q3 2025** | LLM‑powered `explain_operator`, `generate_operator` | Planned |
| **🛡 Q3 2025** | Namespaces & permission layer | Planned |
| **🔄 Q4 2025** | Persistent instances + cleanup hooks | Planned |

---

## 10. Glossary

| Term | Meaning |
|------|---------|
| **atomic_static** | Встроенный Python‑тул в репозитории |
| **atomic_dynamic** | Оператор, созданный через API в рантайме |
| **composite** | Оператор, описанный цепочкой транзакций + scope |
| **scope** | Сегмент общего контекста, доступный всем транзакциям |
| **interpreter** | Среда выполнения кода (`python`, `node`, `llm`, …) |

---

© 2025 Alexander & DAPI team — Deep human‑AI computation.
