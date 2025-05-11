from typing import List, Dict, Any

from lib import (
	O,
	Operator,
	Agent
)
from client.schemas import (
	LocationSchema
)


class Locations(Agent):

	class InputType(O):
		title  : str
		genre  : str
		idea   : str
		spread : int

	class OutputType(O):
		locations : list[LocationSchema]

	template = '''
		Ты хороший рассказчик любящий описывать разные места.
		Твой рассказ на тему "{{title}}" в жанре "{{genre}}".
		Его идея: 
		{{idea}}
		
		Создай {{spread}} локации для развёртки сюжета в духе идеи рассказа.
		Спасибо.
	'''

	async def invoke(self, title, genre, idea, spread):
		return await self.ask(
			self.fill(
				self.template,
				title  = title,
				genre  = genre,
				idea   = idea,
				spread = spread
			)
		)