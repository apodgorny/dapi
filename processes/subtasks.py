from dapi.lib import Datum, Operator
from typing   import Any

class TaskSplitter(Operator):
	'''Splits a given task description into a dynamic number of subtasks.'''

	class InputType(Datum.Pydantic):
		spread      : int
		item        : str
		breadcrumbs : list[str]

	class OutputType(Datum.Pydantic):
		items      : list[str]

	code = '''
		You are assisting a user in breaking down tasks into smaller actionable steps.

		User has narrowed down his task to {{breadcrumbs}}.
		And now has to "{{item}}".

		Your goal:
		- Think of exactly {{spread}} meaningful subtasks that would {{item}}
		- Each subtask must be a smaller, distinct, actionable step.
		- **Do NOT simply restate the original task.**
		- If necessary, be creative to divide the task into reasonable parts.
		- Each subtask should be concise yet informative.
		- Return the result as a list of exactly {{spread}} subtask texts.
	'''

	interpreter = 'llm'
	config = {
		'model_id'    : 'ollama::gemma3:4b',
		'temperature' : 0.2,
	}

################################################################

class Main(Operator):
	'''Entry point that launches recursive task generation.'''

	class InputType(Datum.Pydantic):
		task   : str
		depth  : int
		spread : int

	class OutputType(Datum.Pydantic):
		result: dict[str, Any]

	async def invoke(self, task: str, depth: int, spread: int):
		result = await recursor(
			generator_name  = 'task_splitter',
			generator_input = { 'item': task },
			depth           = depth,
			spread          = spread
		)
		return result

################################################################

class Process:
	entry = Main
