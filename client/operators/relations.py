import os, sys, json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib import (
	O,
	Agent
)

from client.schemas import PersonaSchema, RelationsSchema, RelationSchema


class Relations(Agent):
	class InputType(O):
		story_id      : str
		character_ids : list[str]

	class Expression(O):
		expression: str

	class OutputType(O):
		relations: RelationsSchema

	template = '''
		Происходит история:
		{{story}}.

		---------------
		Ты — персонаж этой истории описанный ниже:
		{{relator}}.

		---------------
		Вот другой персонаж истории:
		{{relatee}}.

		---------------
		Напиши одним искренним предложением от первого лица, как ты к нему/ней относишься.  
		Это должно быть внутреннее эмоциональное, моральное или личностное суждение.  
		Учитывай свой пол, возраст, жизненный опыт и характер.  
		Не повторяй то, что мог бы сказать этот человек о тебе.  
		Не пересказывай факты — вырази **живую внутреннюю реакцию**.
	'''

	async def invoke(self, story_id: str, character_ids: list[str]):
		characters = []
		story_data = await read_json(f'story.{story_id}.json')

		for char_id in character_ids:
			char_data = await read_json(f'persona.{char_id}.json')
			characters.append(char_data)

		relations = []

		for relator in characters:
			for relatee in characters:
				if relator['id'] == relatee['id']:
					continue  # skip self

				prompt = self.fill(
					self.template,
					story   = story_data,
					relator = relator,
					relatee = relatee
				)

				expression = await self.ask(prompt=prompt, schema=self.Expression)

				relations.append({
					'relator_id' : relator['id'],
					'relatee_id' : relatee['id'],
					'expression' : expression
				})
				result = {'relations' : relations }
				await write_json(f'relations.{story_id}.json', result)

		return result