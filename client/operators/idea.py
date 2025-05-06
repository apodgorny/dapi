from pydantic             import BaseModel
from typing               import List, Dict, Any

from lib import (
	O,
	Operator,
	Agent,
	AgentOnGrid,
)


class Idea(AgentOnGrid):

	class InputType(O):
		topic : str
		theme : str

	class OutputType(O):
		idea : str

	template = '''
		Ты талантливый писатель специализирующийся на непредсказуемых и захватывающих сюжетах.
		Твой рассказ на тему "{{topic}}" в жанре "{{theme}}". Придумай общую захватывающую идею и вырази её в 3–4 предложениях. Пожалуйста, оформи ТОЛЬКО идею в JSON-формате.
		
		Спасибо.
	'''

	async def invoke(self, topic, theme):
		return await self.ask(
			self.fill(
				self.template,
				topic = topic,
				theme = theme
			)
		)