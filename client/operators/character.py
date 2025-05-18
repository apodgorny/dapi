from lib import (
	O,
	Operator,
	Agent,
	Respin
)
from client.schemas import (
	BeatSchema
)


class Character(Respin):
	class InputType(O):
		story_id     : str
		character_id : str
		beats        : list[BeatSchema]

	class OutputType(O):
		beat : BeatSchema

	class Templates:
		spin_in = '''
			Ты — {{name}}, {{sex}} в возрасте {{age}} лет.
			Твоё занятие: {{occupation}}.
			Твоё описание:
			{{look}}. {{portrait}}
			Твоя боль жизни: {{pain}}.
			Твоё главное желание: {{desire}}.
			Твоя долгосрочная цель: {{mission}}
			
			Недавние события:
			{{beats}}
		'''
		spins = [
			'''
				Что произошло в "недавних событиях"?
				Как ты можешь использовать их для достижения своих целей/желаний?
				Ответь в 2-4 предложения.
			''',
			'''
				Как ты можешь использовать ситуацию для достижения своих желаний и целей?
				Начни с "Я хочу ..."
				НЕ ПОВТОРЯЙ ВОПРОС,
				ОТВЕТЬ В ОДНО ПРЕДЛОЖЕНИЕ.
			'''
		]
		spin_out = '''
			Скажи фразу и соверши действие, которое приблизит тебя к твоей цели и покажет твою силу или уязвимость.
			Действие — физическое, провоцирующее, интимное или властное (например: прикоснуться, приблизиться, оттолкнуть, поцеловать, передвинуть предмет).
			Отвечай на фразы/действия обращенные к тебе. Не предлагай действие - действуй фразой.
			
			Фраза — короткая, дерзкая или провокационная.
			Действие — смелое и однозначное.

			НЕ ПОВТОРЯЙ ВОПРОС.
			НЕ ОПИСЫВАЙ ДЕЙСТВИЯ ДРУГИХ ПЕРСОНАЖЕЙ
		'''

	async def invoke(self, story_id, character_id, beats):
		dossier = await read_json(f'persona.{character_id}.json')
		story   = await read_json(f'story.{story_id}.json')
		data    = { **dossier, **story }

		line = await self.spin(
			verbose = True,
			beats = beats,
			** data,
		)
		return BeatSchema(
			character_id = character_id,
			line         = line
		)
	 