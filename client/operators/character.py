from lib import (
	O,
	Operator,
	Agent
)


class Character(Agent):
	class InputType(O):
		name : str

	class OutputType(O):
		line : str

	t = '''
		Ты — {{name}}, {{sex}} в возрасте {{age}} лет.
		Твоё занятие: {{occupation}}.
		Твоё описание:
		{{look}}. {{portrait}}
		Твоя боль жизни: {{pain}}.
		Твоё главное желание: {{desire}}.
		Твоя роль: {{role}}.
		Ты находишься в {{location}}.
		Твоя долгосрочная цель: {{mission}}
		Твоё текущее состояние: {{mood}}

		Отношения с другими:
		{{relationships}}

		Недавние события:
		{{beats}}

		Доступные действия: {{actions}}
		Ты можешь ничего не предпринимать — или выбрать два действия.

		Всегда оставайся верен своей природе. Реагируй так, как требует твоя цель и внутреннее состояние.
		Ответь одной-двумя фразами, как если бы ты писал своё действие в сценический скрипт.
		Оставь тишину, в которую смогут войти другие.
	'''

	async def invoke(self, name):
		actions = 'думать чувствовать наблюдать говорить идти выражать делать'.split()
		dossier = await read_json(f'persona.{name.lower().replace(" ", "_")}.json')
		story   = await read_json('story.json')
		prompt  = self.fill(
			self.t,
			name    = name,
			actions = actions,
			beats   = story['beats']
			** dossier
		)
		return await self.ask(prompt)