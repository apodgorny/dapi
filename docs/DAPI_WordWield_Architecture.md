# DAPI and WordWield Architecture Overview

This document provides a detailed architectural overview of the DAPI (Dynamic API) and WordWield components, explaining their structure, interactions, and how they are used within the system.

## Table of Contents

1. [System Overview](#system-overview)
2. [DAPI Core Architecture](#dapi-core-architecture)
   - [Core Components](#core-components)
   - [Services Layer](#services-layer)
   - [Execution Model](#execution-model)
   - [Error Handling](#error-handling)
3. [WordWield Architecture](#wordwield-architecture)
   - [Core Components](#wordwield-core-components)
   - [Operator Pattern](#operator-pattern)
   - [Integration with DAPI](#integration-with-dapi)
4. [Key Workflows](#key-workflows)
   - [Operator Registration](#operator-registration)
   - [Operator Execution](#operator-execution)
   - [Context Tracking](#context-tracking)
5. [Restricted vs Unrestricted Operators](#restricted-vs-unrestricted-operators)
   - [Security Model](#security-model)
   - [Operator Sources](#operator-sources)
   - [Restricted Features](#restricted-features)
6. [Special Methods and Features](#special-methods-and-features)
   - [call() Method](#call-method)
   - [ask() Method](#ask-method)
   - [Model Integration](#model-integration)
7. [Example Operator Patterns](#example-operator-patterns)
   - [Simple Operators](#simple-operators)
   - [Agent Operators](#agent-operators)
   - [Recursive Operators](#recursive-operators)
8. [Directory Structure](#directory-structure)

## System Overview

DAPI (Dynamic API) is a framework for defining and executing operators - reusable units of code that can be dynamically loaded, executed, and composed. WordWield is a client library that provides a more user-friendly interface for interacting with DAPI. Together, they form a powerful system for building and composing modular, executable components.

The system is built around the concept of "operators" - self-contained units that:
- Have well-defined inputs and outputs (enforced through Pydantic schemas)
- Can be executed in isolation or composed together
- Support both synchronous and asynchronous execution patterns
- Can be restricted for security when needed

## DAPI Core Architecture

### Core Components

#### `Dapi` Class (`dapi/lib/dapi.py`)

The central coordinator that:
- Initializes services and the database
- Manages the API router
- Integrates with FastAPI
- Serves as a container for all registered services

```python
class Dapi:
    def __init__(self, *services):
        self.router = APIRouter(prefix='/dapi')
        self.db = SessionLocal()
        # Services are registered here
        # ...
```

#### `DapiService` Base Class (`dapi/lib/dapi.py`)

Abstract base class for all services:
- Provides exception wrapping functionality
- Standardizes initialization behavior
- Connects services to the main Dapi instance

```python
class DapiService:
    '''Base service with exception-wrapping decorator.'''
    def __init__(self, dapi):
        self.dapi = dapi
    # ...
```

#### `ExecutionContext` (`dapi/lib/execution_context.py`)

Tracks the execution flow through operators:
- Maintains an execution stack with frames
- Records information about each operator call (name, line number, restrictions)
- Provides formatted debugging output
- Manages indentation for nested calls

```python
class ExecutionContext:
    def __init__(self, enable_color=True, enable_code=True, importance=0.5):
        self._root = Frame(name='root', lineno=0, restrict=True)
        self._stack = [self._root]
        # ...
```

#### `Python` Interpreter (`dapi/lib/python.py`)

Provides safe execution of operator code:
- Analyzes AST to detect dangerous calls
- Rewrites calls for tracking and security
- Applies restrictions to execution environment
- Manages operator instantiation and invocation

```python
class Python:
    BLOCKED_CALLS = {'eval', 'exec', 'getattr', 'setattr', '__import__'}
    BLOCKED_ATTRS = {'__dict__', '__class__', '__globals__', '__code__'}
    # ...

    def __init__(self, operator_name, operator_class_name, input_dict, code, 
                 execution_context, operator_globals, call_external_operator, restrict=True):
        # ...
    
    async def invoke(self):
        # Initialize, execute the operator, and return result
        # ...
```

#### `Operator` Base Class (`dapi/lib/operator.py`)

The fundamental interface for all operators:
- Defines the contract for inputs and outputs
- Provides access to execution context and globals
- Implements common operator functionality
- Supports agent-specific features like `ask()`

```python
class Operator:
    '''Base interface for any executable operator: static, dynamic, composite.'''
    
    async def invoke(self) -> Datum:
        '''Execute operator and return output Datum.'''
        raise NotImplementedError('Operator must implement invoke method')
    # ...
```

### Services Layer

#### `DefinitionService` (`dapi/services/definition_service.py`)

Manages operator definitions:
- Stores and retrieves operator metadata and code
- Validates operator names and schemas
- Handles plugin loading from the filesystem
- Enforces security restrictions

```python
class DefinitionService(DapiService):
    '''Stores and manages operator definitions, including plugin loading and schema validation.'''
    
    async def create(self, schema: OperatorSchema, replace=False) -> bool:
        # Validate and store an operator definition
        # ...

    async def register_plugin_operators(self):
        # Load operators from the filesystem
        # ...
```

#### `RuntimeService` (`dapi/services/runtime_service.py`)

Handles operator execution:
- Manages operator input/output packing
- Provides the execution environment
- Handles external operator calls
- Validates inputs and outputs against schemas

```python
class RuntimeService(DapiService):
    '''Handles execution of operators: input/output packing, invocation, context tracing.'''
    
    async def invoke(self, name: str, input: dict, context: ExecutionContext) -> dict:
        # Set up environment, execute operator, handle results
        # ...

    async def call_external_operator(self, name: str, args: list, kwargs: dict, context: ExecutionContext) -> Any:
        # Handle calls between operators
        # ...
```

### Execution Model

DAPI implements a secure execution model for operators:

1. **Code Analysis**: Before execution, operator code is analyzed for potentially dangerous constructs
2. **AST Rewriting**: Calls are rewritten to be tracked and executed through a controlled interface
3. **Execution Environment**: A restricted set of globals is provided to the operator code
4. **Context Tracking**: All calls are tracked with an execution context that maintains a call stack
5. **Error Handling**: Exceptions are wrapped with detailed context for debugging

### Error Handling

The DAPI system uses `DapiException` for standardized error handling:
- Errors are categorized by severity ('fyi', 'beware', 'halt')
- Exceptions include detailed context (operator, line number, file)
- The system provides structured error responses with debugging information
- Services wrap public methods with exception handling

## WordWield Architecture

WordWield serves as a client library for interacting with DAPI, providing a more user-friendly interface.

### WordWield Core Components

#### `WordWield` Class (`wordwield/wordwield.py`)

Main interface for creating and invoking operators:
- Provides methods for operator registration and invocation
- Handles HTTP communication with DAPI
- Formats error messages and responses
- Simplifies operator definition workflow

```python
class WordWield:
    @staticmethod
    def create_operator(operator_class):
        # Serialize and register an operator with DAPI
        # ...

    @staticmethod
    def invoke(name: str, *args, **kwargs):
        # Invoke an operator through DAPI
        # ...
```

#### `String` Utility (`wordwield/string.py`)

Provides string manipulation and formatting:
- Case conversion (camel, snake, etc.)
- Color formatting for terminal output
- String alignment and padding
- Text highlighting and formatting

#### `Highlight` Utility (`wordwield/highlight.py`)

Handles syntax highlighting for code and data:
- Syntax highlighting for Python code
- JSON/YAML data formatting
- Terminal color handling
- Output prettification

#### `Datum` Utility (`wordwield/datum.py`)

Manages data structures and schema validation:
- Converts between different data formats
- Validates data against schemas
- Handles type conversion and checking
- Supports serialization/deserialization

### Operator Pattern

Both DAPI and WordWield revolve around the Operator pattern:

1. **Definition**: Operators are defined as classes inheriting from `Operator` with:
   - `InputType`: Pydantic model defining input fields and types
   - `OutputType`: Pydantic model defining output fields and types
   - `invoke()` method: Asynchronous method implementing the operator's logic

2. **Registration**: Operators are registered with DAPI through:
   - File-based plugins loaded from the operators directory
   - Dynamic registration via API calls
   - WordWield's simplified registration helpers

3. **Invocation**: Operators are executed through:
   - Direct API calls to DAPI
   - Calls from within other operators
   - WordWield's client interface

### Integration with DAPI

WordWield integrates with DAPI through its HTTP API:
- Creates operators by serializing Python classes
- Invokes operators by sending requests with input data
- Handles responses and errors from DAPI
- Provides a simpler interface for defining and using operators

## Key Workflows

### Operator Registration

1. **Define Operator Class**:
   ```python
   class MyOperator(Operator):
       class InputType(BaseModel):
           name: str
           
       class OutputType(BaseModel):
           greeting: str
           
       async def invoke(self, name):
           return {"greeting": f"Hello, {name}!"}
   ```

2. **Register with DAPI**:
   - Via WordWield: `WordWield.create_operator(MyOperator)`
   - Via DAPI API: POST to `/dapi/create_operator`
   - Via filesystem: Place in operators directory for auto-loading

3. **Storage**:
   - Operator is stored in the database by DefinitionService
   - Code, input/output schemas, and metadata are preserved

### Operator Execution

1. **Invocation Request**:
   - Via WordWield: `WordWield.invoke("my_operator", name="World")`
   - Via DAPI API: POST to `/dapi/my_operator` with input data
   - Via another operator: `await call("my_operator", name="World")`

2. **Execution Process**:
   1. RuntimeService retrieves operator definition
   2. Input is validated against InputType schema
   3. Python interpreter sets up execution environment
   4. Operator code is executed with tracking
   5. Output is validated against OutputType schema
   6. Result is returned to caller

### Context Tracking

During operator execution, DAPI maintains detailed context:

1. Each operator call pushes a new frame to the execution stack
2. Nested calls create a hierarchical context structure
3. Line numbers and operator names are tracked
4. On error, the full context is available for debugging
5. When execution completes, frames are popped from the stack

## Restricted vs Unrestricted Operators

DAPI implements a security model that classifies operators as either "restricted" or "unrestricted" to control their capabilities and potential impact on the system.

### Security Model

The restriction system provides a security boundary that limits what operators can do:

- **Restricted Operators**: Run in a sandboxed environment with limitations on available functions and properties to prevent potentially harmful operations.
- **Unrestricted Operators**: Run with fewer restrictions, allowing access to more capabilities but requiring higher trust.

The Python interpreter implements these restrictions through AST analysis and code transformation:

```python
# From dapi/lib/python.py
def _initialize(self):
    # ...
    if self.restrict:
        print('---RESTRICT', self.operator_name)
        tree = ast.parse(self.code, filename='<python>')
        self._detect_dangerous_calls(tree)
        compiled = self._rewrite_calls(self.code)
        self._apply_restrictions(self.globals)
    else:
        print('---NOT RESTRICT', self.operator_name)
        compiled = compile(self.code, filename='<python>', mode='exec')
    # ...
```

### Operator Sources

Operators come from different sources, which affects their restriction status:

1. **File-based Operators**: Operators loaded from the file system during initialization are considered trusted and marked as unrestricted.

   ```python
   # From dapi/services/definition_service.py
   async def register_plugin_operators(self):
       await self.delete_all()
       classes = Module.load_package_classes(Operator, OPERATOR_DIR)

       print(String.underlined('\nUnrestricted operators:'))
       for name, operator_class in classes.items():
           # ...
           schema = OperatorSchema(
               # ...
               restrict = False,  # File-based operators are unrestricted
               # ...
           )
   ```

2. **API-created Operators**: Operators created via the API are considered potentially untrusted and marked as restricted by default.

### Restricted Features

When an operator is marked as restricted, several security measures are applied:

1. **Blocked Function Calls**: Certain high-risk functions are blocked:
   ```python
   BLOCKED_CALLS = {'eval', 'exec', 'getattr', 'setattr', '__import__'}
   ```

2. **Blocked Attributes**: Access to potentially dangerous attributes is prevented:
   ```python
   BLOCKED_ATTRS = {'__dict__', '__class__', '__globals__', '__code__'}
   ```

3. **Limited Globals**: The global environment has restricted access to built-in functions:
   ```python
   BLOCKED_GLOBALS = [
       '__import__', 'eval', 'exec', 'open', 'compile', 'globals', 'locals',
       'vars', 'getattr', 'setattr', 'delattr', 'super', 'type', 'object', 'dir'
   ]
   ```

4. **Call Rewriting**: All function calls in restricted operators are rewritten to pass through a controlled interface that:
   - Tracks the call chain for debugging
   - Applies security policies
   - Validates inputs and outputs
   - Updates the execution context

The Python interpreter enforces these restrictions through AST (Abstract Syntax Tree) analysis:

```python
def _detect_dangerous_calls(self, tree: ast.AST):
    class DangerousCallDetector(ast.NodeVisitor):
        def visit_Import(self, node):
            raise ValueError('Use of `import` is not allowed')

        def visit_ImportFrom(self, node):
            raise ValueError('Use of `from ... import` is not allowed')

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id in Python.BLOCKED_CALLS:
                raise ValueError(f'Use of `{node.func.id}` is not allowed')
            self.generic_visit(node)

        def visit_Attribute(self, node):
            if node.attr in Python.BLOCKED_ATTRS:
                raise ValueError(f'Access to `{node.attr}` is not allowed')
            self.generic_visit(node)

    DangerousCallDetector().visit(tree)
```

When working with restricted operators, the Python interpreter provides a controlled set of allowed globals:

```python
ALLOWED_GLOBALS = {
    'int': int, 'float': float, 'str': str, 'bool': bool,
    'dict': dict, 'list': list, 'tuple': tuple, 'len': len,
    'range': range, 'enumerate': enumerate, 'zip': zip,
    'sum': sum, 'min': min, 'max': max, 'print': print
}
```

The restriction system ensures that potentially untrusted code can be executed safely within the DAPI environment while still allowing trusted operators to have the capabilities they need.

## Special Methods and Features

### call() Method

The `call()` method allows operators to invoke other operators from within their code. It's a core mechanism for operator composition and is available globally in the operator's execution environment.

```python
# Calling from within an operator
async def invoke(self, input_param):
    # Call another operator and wait for its result
    result = await call('other_operator', param1='value1', param2='value2')
    
    # Or with a dict instead of keyword arguments
    result = await call('other_operator', {'param1': 'value1', 'param2': 'value2'})
    
    # Process the result
    return processed_result
```

Implementation in Runtime Service:

```python
async def _call(name, *args, **kwargs):
    if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
        kwargs = args[0]
        args   = []

    return await self.call_external_operator(
        name     = name,
        args     = list(args),
        kwargs   = kwargs,
        context  = context
    )
```

Example usage (from processes/call_test.py):

```python
class Main(Operator):
    class InputType(BaseModel):
        operator : str
        message  : str

    class OutputType(BaseModel):
        call_result : dict

    async def invoke(self, operator, message):
        return await call(operator, message)
```

### ask() Method

The `ask()` method is used for invoking AI models (LLMs) to process data. It exists in two forms:

1. **Global `ask()`**: Available to all operators through the execution environment
2. **`self.ask()`**: A convenience method for agent operators with defined prompts

Implementation details:

```python
# Global ask() function (in runtime_service.py)
async def _ask(
    input,
    prompt,
    response_schema,
    model_id    = 'ollama::gemma3:4b',
    temperature = 0.0
):
    return await Model.generate(
        prompt          = prompt,
        input           = input,
        response_schema = response_schema,
        model_id        = model_id,
        temperature     = temperature
    )

# Operator's self.ask() method (in operator.py)
async def ask(self, *args, **kwargs):
    if not hasattr(self, 'prompt'):
        raise ValueError('Method call self.ask is only allowed for agent operators (self.prompt must be defined)')

    # ask({ ... })
    if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
        input = args[0]
    else:
        input = kwargs

    return await self.globals['ask'](
        input           = input,
        prompt          = self.prompt,
        response_schema = self.output_type
    )
```

#### Differences between `ask()` and `self.ask()`

There are important differences between the global `ask()` function and the `self.ask()` method:

| Feature | Global `ask()` | `self.ask()` |
|---------|---------------|--------------|
| **Availability** | Available in any operator's execution environment | Only works in operators with a defined `prompt` attribute |
| **Usage context** | Can be used in any operator with any prompt | Specifically designed for agent operators |
| **Parameters** | Requires explicit prompt, input, and response schema | Only needs input parameters, uses operator's predefined prompt and output type |
| **Template access** | Requires manual template handling | Automatically resolves `{{placeholder}}` values from the operator's prompt |
| **Schema validation** | Requires explicit schema definition | Automatically uses the operator's OutputType for validation |

Here's how `self.ask()` is used in the OllamaAddOne example from processes/all.py:

```python
class OllamaAddOne(Operator):
    class InputType(BaseModel):
        x: float

    class OutputType(BaseModel):
        x: float

    prompt = '''
        'Given a number {{x}}, return its increment by one as { "x": x + 1 }'
    '''

    async def invoke(self, x):
        return await self.ask(x = x)
```

In this example:
1. The operator defines a `prompt` attribute with a template using `{{x}}` as a placeholder
2. In the `invoke` method, `self.ask(x = x)` is called, which:
   - Passes the `x` value to be inserted into the prompt template
   - Uses the operator's predefined prompt with the placeholder replaced by the actual value
   - Validates the LLM response against the OutputType schema
   - Returns the validated response

This approach makes agent operators much cleaner and easier to write compared to using the global `ask()` function directly, which would require:

```python
# Equivalent using global ask() - much more verbose
result = await ask(
    input = {'x': x},
    prompt = 'Given a number {{x}}, return its increment by one as { "x": x + 1 }',
    response_schema = self.output_type,
    model_id = 'ollama::gemma3:4b'  # would need to specify this too
)
```

Example of an operator that combines multiple execution models (from processes/all.py):

```python
class DoubleThenSquare(Operator):
    class InputType(BaseModel):
        x: float

    class OutputType(BaseModel):
        x: float

    async def invoke(self, x):
        # exec('x = 2')  # Would be blocked in restricted mode
        print('%'*10)
        x = await times_two(x)       # Full Python
        x = await square(x)          # Mini Python
        x = await ollama_add_one(x)  # LLM
        return x
```

This example demonstrates a chain of operator calls, combining regular operators with LLM-powered ones. The example also shows a commented-out `exec()` call that would be blocked in restricted mode, illustrating the security features of DAPI.

### Model Integration

DAPI provides integrated AI model support:

- Models are accessed via the `Model.generate()` method
- The system supports multiple model providers (OpenAI, Ollama)
- Agent operators can interact with models via `ask()` method
- Prompt templating is available for dynamic prompt generation
- Structured outputs are validated against the operator's OutputType schema

## Example Operator Patterns

### Simple Operators

Basic operators that perform straightforward computations or operations:

```python
class Disp(Operator):
    class InputType(BaseModel):
        s: str

    class OutputType(BaseModel):
        s: str

    async def invoke(self, s):
        return print('==========> DISP-', s)
```

### Agent Operators

Operators that leverage LLMs to process data:

```python
class OllamaAddOne(Operator):
    class InputType(BaseModel):
        x: float

    class OutputType(BaseModel):
        x: float

    prompt = '''
        'Given a number {{x}}, return its increment by one as { "x": x + 1 }'
    '''

    async def invoke(self, x):
        return await self.ask(x = x)
```

This simple example shows how `self.ask()` is used to delegate the computation to an LLM, passing the input parameter and using a prompt template with the `{{x}}` placeholder that gets replaced with the actual value. The result is automatically validated against the OutputType schema.

### Recursive Operators

Operators that call themselves or other operators recursively:

```python
class Recurse(Operator):
    class InputType(BaseModel):
        s: str
        n: int

    class OutputType(BaseModel):
        s: str

    async def invoke(self, s, n):
        if n > 0:
            await disp(s + f' ({n})')
            await recurse(s, n - 1)
            
        return s
```

A more complex example (from operators/recursor.py):

```python
class Recursor(Operator):
    '''Recursively calls an operator and builds a tree structure using its list output.''' 

    class InputType(BaseModel):
        generator_name  : str
        generator_input : dict
        depth           : int
        spread          : int
        breadcrumbs     : list[str] = None

    class OutputType(BaseModel):
        value : dict

    async def invoke(
        self,
        generator_name  : str,
        generator_input : dict,
        depth           : int       = 1,
        spread          : int       = 1,
        breadcrumbs     : list[str] = None
    ):
        breadcrumbs = breadcrumbs or []
        breadcrumbs = breadcrumbs.copy()
        result = {
            'in'  : generator_input['item'],
            'out' : []
        }
        if depth > 0:
            print(breadcrumbs)
            generator_input = { **generator_input, 'spread': spread, 'breadcrumbs' : breadcrumbs }
            call_result     = await call(generator_name, generator_input)

            breadcrumbs.append(generator_input['item'])

            if depth > 1:
                for item in call_result:
                    new_generator_input = {
                        **generator_input,     # keep all old keys
                        'item'        : item,  # update only item
                        'breadcrumbs' : breadcrumbs
                    }
                    result_item = await recursor(
                        generator_name  = generator_name,
                        generator_input = new_generator_input,
                        depth           = depth-1,
                        spread          = spread,
                        breadcrumbs     = breadcrumbs
                    )
                    result['out'].append({'in': item, 'out': result_item['out']})
            else:
                for item in call_result:
                    result['out'].append({'in': item, 'out': []})
        return result
```

Example of a composition operator using both call() and agent patterns (from processes/story.py):

```python
class Story(Operator):
    class InputType(BaseModel):
        topic  : str
        depth  : int
        spread : int

    class OutputType(BaseModel):
        root: dict

    async def invoke(self, topic, depth, spread):
        idea = await idea(topic)
        print('IDEA:', idea)
        planner_input = {
            'topic' : topic,
            'idea'  : idea,
            'item'  : topic
        }
        result = await recursor(
            generator_name  = 'planner',
            generator_input = planner_input,
            depth           = depth,
            spread          = spread
        )
        return result
```

## Directory Structure

```
dapi/
├── app.py                 # FastAPI application setup
├── controller.py          # API endpoints and routing
├── db.py                  # Database models and connection
├── process.py             # Process management
├── schemas.py             # API schemas
├── lib/                   # Core library components
│   ├── dapi.py            # Main DAPI class
│   ├── operator.py        # Base Operator class
│   ├── python.py          # Secure Python interpreter
│   ├── execution_context.py # Execution tracking
│   ├── datum.py           # Data handling
│   └── ...
├── services/              # Service layer
│   ├── definition_service.py # Operator definition management
│   ├── runtime_service.py    # Operator execution
│   └── ...
├── models/                # AI Model integrations
│   ├── model_ollama.py    # Ollama model integration
│   ├── model_openai.py    # OpenAI model integration
│   └── ...
└── middleware/            # API middleware
    └── openapi.py         # OpenAPI enhancement

wordwield/
├── wordwield.py           # Main WordWield client
├── string.py              # String utilities
├── highlight.py           # Code highlighting
├── datum.py               # Data structure handling
└── operator.py            # Operator utilities
```

This architecture enables a powerful, composable system for defining and executing code components with strong typing, security, and debugging capabilities.
