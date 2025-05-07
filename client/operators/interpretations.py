from pydantic             import BaseModel
from typing               import List, Dict, Any

from lib import (
	O,
	Operator,
	Agent,
	AgentOnGrid,
)


class Interpretations(Agent):
	class InputType(O):
		title  : str
		theme  : str
		spread : int

	class OutputType(O):
		title : str

	class Interpretations(O):
		items: list[str]

	template = '''
		Создай {{spread}} интерпретаций заголовка "{{title}}" в стиле "{{theme}}", 3-4 слова каждый.
	'''

	async def invoke(self, title, theme, spread=10):
		prompt = self.fill(
			self.template,
			title  = title,
			theme  = theme,
			spread = spread
		)
		interpretations = await self.ask(
			prompt,
			schema = self.Interpretations
		)
		return random.choice(interpretations)