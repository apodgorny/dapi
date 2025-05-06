
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pydantic             import BaseModel
from typing               import List, Dict, Any

from lib import (
	Operator,
	Agent,
	AgentOnGrid,
)

# Import from client.schemas package
from client.schemas import Persona


class Protogonist(Agent):
	class InputType(BaseModel):
		title : str
		idea  : str
		theme : str

	class OutputType(BaseModel):
		persona: Persona

	template = '''
		Ты писатель. Пишешь книгу под названием "{{title}}".
		Идея книги: "{{idea}}".
		Извлеки главного персонажа из идеи.
		Персонаж должен хорошо вписываться в жанр {{theme}}.
		Используй русские имена.
		Создай имя соответствующее полу.
		Прояви креативность.
		Представь результат в формате JSON:
	''' + '{ persona: ' + Persona.prompt() + '}'

	async def invoke(self, title, idea, theme):
		print(Persona, builtins.type(Persona))
		prompt = self.fill(
			self.template,
			title = title,
			idea  = idea,
			theme = theme
		)
		print(prompt)
		return await self.ask(prompt=prompt)
