from pydantic             import BaseModel
from typing               import List, Dict, Any

from lib import (
	Operator,
	Agent,
	AgentOnGrid,
)


class Interpretations(Agent):
	class InputType(BaseModel):
		title  : str
		theme  : str
		spread : int

	class OutputType(BaseModel):
		title : str

	class Interpretations(BaseModel):
		items: list[str]

	prompt = '''
		Создай {{spread}} интерпретаций заголовка "{{title}}" в стиле "{{theme}}", 3-4 слова каждый.
	'''

	async def invoke(self, title, theme, spread=10):
		prompt = self.fill(
			self.prompt,
			title  = title,
			theme  = theme,
			spread = spread
		)
		interpretations = await self.ask(
			prompt,
			schema = self.Interpretations
		)
		print(prompt)
		print(interpretations)
		return random.choice(interpretations)