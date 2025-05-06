import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pydantic             import BaseModel
from typing               import List, Dict, Any

from lib import (
	Agent, O
)

# Import from client.schemas package
from client.schemas import Persona


class Antagonist(Agent):
	class InputType(O):
		title     : str
		idea      : str
		theme     : str
		character : Persona  # protagonist

	class OutputType(O):
		persona: Persona

	template = '''
		Ты писатель. Твоя задача — создать персонажа **антагониста**
		для книги под названием "{{title}}".

		Идея книги: "{{idea}}"
		Жанр: {{theme}}

		Вот ключевой персонаж, который уже присутствует в истории:
		{{character}}

		Создай антагониста, который будет драматически контрастировать с ним:
		- Их цели должны конфликтовать
		- Их мировоззрение должно отличаться
		- Он или она должны вызывать эмоциональное или моральное напряжение
		- Подумай, кто сильнее всего триггернёт этого героя — антагонист мужчина или женщина?
		- Создай имя соответствующее полу.

		Сделай антагониста эмоционально насыщенным и повествовательно мощным.
		Не упоминай другого персонажа в описании антагониста.
		Используй русские имена. Имя должно отличаться от ключевого персонажа и соответствовать полу.
	'''

	async def invoke(self, title, idea, theme, character):
		prompt = self.fill(
			self.template,
			title     = title,
			idea      = idea,
			theme     = theme,
			character = character
		)
		return await self.ask(prompt=prompt)
