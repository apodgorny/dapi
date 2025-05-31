from pydantic             import BaseModel
from typing               import List, Dict, Any

from lib import (
	O,
	Operator,
	Agent,
	Expert,
)


class Writer(Agent):

	class InputType(O):
		title     : str
		genre     : str
		idea      : str
		questions : list[str]
		spread    : int

	class Answer(O):
		answer: str

	class OutputType(O):
		answers: list[str]

	template = '''
		Ты опытный писатель и пишешь рассказ "{{title}}" в жанре "{{genre}}"
		Сюжет рассказа:
		------------
		{{idea}}
		------------
		Напиши {{spread}} предложений отвечающих на вопрос по сюжету: {{question}}
		Ответь так, чтобы это максимально развлекло читателя.
		Спасибо
	'''

	async def invoke(self, title, genre, idea, questions, spread=3):
		answers = []
		for question in questions:
			prompt = self.fill(
				self.template,
				title    = title,
				genre    = genre,
				idea     = idea,
				question = question,
				spread   = spread
			)
			answer = await self.ask(
				prompt = prompt,
				schema = self.Answer
			)
			answers.append(answer)
		return answers



		# return await self.ask(
		# 	self.fill(
		# 		self.template,
		# 		idea     = idea,
		# 		question = question,
		# 		spread   = spread
		# 	)
		# )