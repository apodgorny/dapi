
import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pydantic             import BaseModel
from typing               import List, Dict, Any

from lib import (
	O,
	Agent,
	String
)

# Import from client.schemas package
from client.schemas import PersonaSchema


class Protogonist(Agent):
	class InputType(O):
		story_id : str

	class OutputType(O):
		persona: PersonaSchema

	template = '''
		Ты талантливый писатель. Вот данные о книге, которую ты пишешь.
		------
		{{story}}
		------
		Извлеки главного персонажа.
		Персонаж должен хорошо вписываться в жанр книги.
		Используй русские имена.
		Создай имя соответствующее полу.
		Прояви креативность.
		Спасибо.
	'''

	async def invoke(self, story_id):
		story_data = await read_json(f'story.{story_id}.json')
		prompt = self.fill(
			self.template,
			story = json.dumps(story_data)
		)
		data = await self.ask(prompt=prompt)
		id   = String.slugify(data['name'])
		data['id'] = id
		await write_json(f'character.{id}.json', data)
		return data
