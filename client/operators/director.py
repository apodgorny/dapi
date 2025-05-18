from lib import (
	O,
	Operator,
	Agent
)
from client.schemas import (
	BeatSchema,
	DirectorBeatSchema,
	StorySchema,
	CharacterSchema
)


class Director(Agent):
	class InputType(O):
		story_id      : str
		character_ids : list[str]
		beats         : list[BeatSchema]

	class OutputType(O):
		beat : DirectorBeatSchema

	t_identity = '''
		История:
		---------------
		{{story}}
		---------------
		Персонажи:
		---------------
		{{characters}}
		---------------
		********************************************************************
		Tы голос директора сцены из-за кулис объявляющий перемену обстановки.
		Ты НЕ ПЕРСОНАЖ, 
		Не повторяй за персонажами, не говори за персонажей.
		********************************************************************
	'''

	t_no_beats = '''
		Сейчас начало новой сцены - задай название сцены, локацию и сеттинг
	'''

	t_beats = '''
		Ты — режиссёр.  
		Ты НЕ персонаж и НЕ участник сцены.  
		Ты НЕ описываешь мысли, действия или ощущения кого-либо.  
		Ты НЕ изображаешь POV ни одного героя.  

		Ты можешь говорить только:
		- Метафорически о пространстве, времени, атмосфере.
		- Сценически о смене обстановки.
		- Лирически о завершении сцены.

		Всё остальное запрещено.

		Запрещённые конструкции:
		- Имя персонажа в начале фразы.
		- "Аня ощутила", "Елисей увидел", "Он почувствовал", "Я..." — запрещено.
		- Любые прямые указания на внутренние состояния героев — запрещено.

		Разрешённые конструкции:
		- "Площадь погрузилась в глухую тишину."
		- "Порывы ветра унесли остатки слов."
		- "Пустота заполнила руины."

		Если сцена ещё жива — не пиши ничего.

		---

		Недавние биты:

		{{beats}}

		Если сцена не требует смены — оставь `"action": ""`, `"cut": false`.
	'''

	async def invoke(self, story_id, character_ids, beats):
		characters = {}
		
		for char_id in character_ids:
			character = await read_json(f'persona.{char_id}.json')
			characters[char_id] = character

		story = await read_json(f'story.{story_id}.json')

		template = self.t_identity + (self.t_beats if beats else self.t_no_beats)

		prompt = self.fill(
			template,
			beats      = beats,
			story      = story,
			characters = characters
		)
		return await self.ask(prompt)