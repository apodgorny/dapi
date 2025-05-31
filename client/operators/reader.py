from pydantic             import BaseModel
from typing               import List, Dict, Any

from lib import (
	O,
	Operator,
	Agent,
	Expert,
)


class Reader(Agent):

	class InputType(O):
		idea   : str
		spread : int

	class OutputType(O):
		questions: list[str]

	template = '''
		Ты любопытный и требовательный читатель предпочитающий логичные но многоуровневые сюжеты.
		Ты хочешь узнать больше про данный рассказ:
		------------
		{{idea}}
		------------
		Сформулируй {{spread}} ВОПРОСОВ, каждый из которых:
			- должен быть законченным и самодостаточным;
			- должен содержать **только один вопрос**, без объединений, под-вопросов и пояснений;
			- должен быть интересным и раскрывающим сюжет.
		Спасибо
	'''

	async def invoke(self, idea, spread=3):
		return await self.ask(
			self.fill(
				self.template,
				idea   = idea,
				spread = spread
			)
		)