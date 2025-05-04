# StateGrid Execution Model

This document defines the core execution flow for `StateGrid`, which powers recursive and contextual agent coordination using `AgentOnGrid`. It is a replacement for hardcoded recursion and YAML-driven workflows, focused entirely on Python-native execution flow.

---

## Overview

- **`StateGrid`** defines a space of possible `State`s and governs transitions between them.
- **`AgentOnGrid`** is a stateless actor that reacts to each `State` through `on_enter`.
- **`StateGridEngine`** is the core orchestrator that executes the grid and coordinates agents.

---

## Core Concepts

### 1. State

Each node in the recursive execution tree is a `State`. It includes:

```python
class State:
	id          : str         # Unique identifier, e.g., "start.0.1"
	depth       : int         # Level in the recursive tree
	breadcrumbs : list[str]   # Path from root
	sctx        : dict        # Shared, horizontal state context
	agent_name  : str         # Name of agent assigned to handle this state
```

### 2. AgentOnGrid

Agents are **stateless** responders. They do not retain memory of recursion depth or siblings.

Each agent implements:

```python
class AgentOnGrid:
	def on_enter(self, state: State) -> AgentResult:
		...

	def on_leave(self, state: State):
		...

	self.engine  # Provided automatically to enable delegation
```

An agent learns its position **only upon entry** to a state.

---

## Execution Flow

### Step-by-step:

1. **Engine starts at root state** (`depth = 0`)
2. Calls `agent.on_enter(state)`
3. Agent returns `AgentResult`:
    - `None` → end of recursion
    - `str` → next agent for current branch
    - `list[str]` → branches: new states created with current agent
    - `dict` → full control: branching, delegation, context override
4. Engine calls `on_agent_done(state, result)`:
    - Creates new states if needed
    - Sets `state.agent_name`
    - Calls next `agent.on_enter(...)`
5. For parallel branches:
    - Each `State` notifies the engine with `notify_ready(state_id)`
    - If `sync_mode=False` (default): child states launched immediately
    - If `sync_mode=True`: waits until all siblings are ready

---

## AgentResult Examples

### Return list (branch):

```python
return ['intro', 'conflict', 'climax']
```

Creates 3 new states under current one.

### Return another agent:

```python
return 'guru'
```

Current branch continues with new agent.

### Return nothing:

```python
return None
```

Marks state as completed.

### Return structured result:

```python
return {
	'branches'  : ['hero', 'villain'],
	'agent'     : 'writer',
	'context'   : { 'mood': 'tense' },
	'continue_in': 'child_state'
}
```

Full control over continuation.

---

## Engine Methods

```python
class StateGridEngine:

	def notify_ready(self, state_id: str): ...
	def on_agent_done(self, state: State, result): ...
	def on_agent_exception(self, state: State, error): ...
```

---

## Summary

This execution model allows:

- Python-native agent orchestration
- Stateless, reusable agents
- Context-aware branching
- Optional synchronization across branches
- Full control over depth/spread structure via agent return values

It replaces YAML-driven recursion with elegant, testable logic inside the agent.

