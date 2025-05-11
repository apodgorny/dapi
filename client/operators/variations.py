from pydantic             import BaseModel
from typing               import List, Dict, Any

from lib import (
	O,
	Operator,
	Agent,
	AgentOnGrid,
)


class Variations(Agent):
	class InputType(O):
		title  : str
		genre  : str
		spread : int

	class OutputType(O):
		variation : str

	class Variations(O):
		items: list[str]

	template = '''
		Создай {{spread}} интерпретаций заголовка "{{title}}" в стиле "{{genre}}", 3-4 слова каждый.
		Будь креативным и изысканным.
	'''

	async def invoke(self, title, genre, spread=10):
		prompt = self.fill(
			self.template,
			title  = title,
			genre  = genre,
			spread = spread
		)
		variations = await self.ask(
			prompt,
			schema = self.Variations
		)
		return random.choice(variations)