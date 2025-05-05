import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic import BaseModel
from typing   import List, Dict, Any

from wordwield.wordwield import Operator, WordWield as ww

################################################################

class TaskSplitter(Operator):
	class InputType(BaseModel):
		spread      : int
		item        : str
		breadcrumbs : list[str]

	class OutputType(BaseModel):
		items: List[str]

	prompt = '''
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

	async def invoke(self, **input):
		return await self.ask(**input)

################################################################

class Main(Operator):
	class InputType(BaseModel):
		task   : str
		depth  : int
		spread : int

	class OutputType(BaseModel):
		result: Dict[str, Any]

	async def invoke(self, task, depth, spread):
		return await recursor(
			generator_name  = 'task_splitter',
			generator_input = { 'item': task },
			depth           = depth,
			spread          = spread
		)

################################################################

ww.init()
result = ww.invoke('main',
	task   = 'Write a book on AI philosophy',
	depth  = 2,
	spread = 2
)

def display_tree(node, indent=0):
	'''Recursively prints a tree based on 'in' fields.'''
	if not node:
		return
	print('    ' * indent + str(node.get('in', '')))
	for child in node.get('out', []):
		display_tree(child, indent + 1)

display_tree(result['output']['result'])
