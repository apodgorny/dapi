from typing import List, Dict, Any

from lib import (
	O,
	Operator,
	Agent
)


class Idea(Agent):

	class InputType(O):
		title     : str
		variation : str
		genre     : str

	class OutputType(O):
		idea : str

	template = '''
		Ты талантливый писатель специализирующийся на непредсказуемых и захватывающих сюжетах.
		Твой рассказ "{{title}}" на тему "{{variation}}" в жанре "{{genre}}".
		Придумай общую захватывающую идею и вырази её в 3–4 предложениях.
		
		Спасибо.
	'''

	async def invoke(self, title, variation, genre):
		return await self.ask(
			self.fill(
				self.template,
				title     = title,
				variation = variation,
				genre     = genre
			)
		)
