import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pydantic             import BaseModel
from typing               import List, Dict, Any

from lib import (
	O,
	Agent,
	String
)

from client.schemas import PersonaSchema


class Antagonist(Agent):
	class InputType(O):
		story_id     : str
		character_id : str

	class OutputType(O):
		persona: PersonaSchema

	template = '''
		Ты талантливый писатель. Вот данные о книге, которую ты пишешь.
		------
		{{story}}
		------
		Твоя задача — создать персонажа **антагониста**
		Вот ключевой персонаж, который уже присутствует в истории:
		------
		{{character}}
		------

		Создай антагониста, который будет драматически контрастировать с ним:
		- Их цели должны конфликтовать
		- Их мировоззрение должно отличаться
		- Он или она должны вызывать эмоциональное или моральное напряжение
		- Подумай, кто сильнее всего триггернёт этого героя — антагонист мужчина или женщина?
		- Найди имя в данных книги или создай имя соответствующее полу.
		- **Не используй имя ключевого персонажа**.

		Сделай антагониста эмоционально насыщенным и повествовательно мощным.
		Не упоминай другого персонажа в описании антагониста.
		Используй русские имена. Имя должно отличаться от ключевого персонажа и соответствовать полу.
	'''

	async def invoke(self, story_id, character_id):
		story_data     = await read_json(f'story.{story_id}.json')
		character_data = await read_json(f'character.{character_id}.json')
		prompt = self.fill(
			self.template,
			story     = json.dumps(story_data),
			character = json.dumps(character_data)
		)
		data = await self.ask(prompt=prompt)
		id   = String.slugify(data['name'])
		data['id'] = id
		await write_json(f'character.{id}.json', data)
		return data
