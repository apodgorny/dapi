from lib import (
	O,
	Operator,
	Agent,
	Spinner
)
from client.schemas import (
	BeatSchema
)


class Character(Spinner):
	class InputType(O):
		story_id     : str
		character_id : str
		beats        : list[BeatSchema]

	class OutputType(O):
		beat : BeatSchema

	t = '''
		Ты — {{name}}, {{sex}} в возрасте {{age}} лет.
		Твоё занятие: {{occupation}}.
		Твоё описание:
		{{look}}. {{portrait}}
		Твоя боль жизни: {{pain}}.
		Твоё главное желание: {{desire}}.
		Твоя долгосрочная цель: {{mission}}

		Недавние события:
		{{digest}}

		Подумай как ты себя чувствуешь, что хочешь сделать или сказать в ответ на недавние события.
		Рагируй на прикосновения, действия, слова, выражения лица.
		Найди способ сказать или сделать что-то такое, что приведет тебя к исполнению твоего секретного желания.
		Действуй в эту сторону телом, речью и умом.

		ОТВЕЧАЙ НА РУССКОМ ЯЗЫКЕ
	'''
	# Твоя роль: {{role}}.
	# Твоё текущее состояние: {{mood}}
	# Ты находишься в {{location}}.
	# Отношения с другими:
	# 	{{relationships}}

	def _pronoun(self, is_subject=True, first_face=True):
		if first_face:
			return 'я' if is_subject else 'мне'
		return 'ты' if is_subject else 'тебе'

	def _id_to_name(self, char_id, own_id, is_subject, first_face):
		if char_id == own_id:
			return self._pronoun(is_subject, first_face)
		return ' '.join(part.capitalize() for part in char_id.replace('-', ' ').split())

	def _targets_to_names(self, own_id, beat, is_subject, first_face):
		target_ids = beat.target_ids or []
		return ', '.join([self._id_to_name(id, own_id, is_subject, first_face) for id in target_ids])

	def _get_outer_expression(self, own_id, beat):
		actor_id     = beat.character_id
		speech       = beat.line.strip()
		expression   = beat.expression.strip()
		action       = beat.action.strip()
		subject_name = self._id_to_name(actor_id, own_id, True, False)
		object_names = self._targets_to_names(own_id, beat, False, False)
		lines        = []

		if speech     : lines.append(f'{subject_name} сказал(а) {object_names}: "{speech}".')
		if expression : lines.append(f'{subject_name} выразил(а) {object_names}: "{expression}".')
		if action     : lines.append(f'{subject_name} сделал(а): "{action}".')

		return lines

	def _get_inner_expression(self, own_id, beat):
		actor_id     = beat.character_id
		feeling      = beat.feeling.strip()
		thought      = beat.thought.strip()
		desire       = beat.desire.strip()
		subject_name = self._id_to_name(actor_id, own_id, True, False)
		lines        = []

		if feeling : lines.append(f'{subject_name} почувствовал(а) "{feeling}".')
		if thought : lines.append(f'{subject_name} подумал(а)      "{thought}".')
		if desire  : lines.append(f'{subject_name} секретно хочет  "{desire}".')

		return lines

	async def get_digest(self, own_id, beats):
		lines = []
		for beat in beats:
			beat = BeatSchema(**beat) if isinstance(beat, dict) else beat
			lines = self._get_outer_expression(own_id, beat)
			if beat.character_id == own_id:
				lines += self._get_inner_expression(own_id, beat)
			lines.append('\n')

		return '\n'.join(lines) if lines else 'Пока ничего примечательного не произошло.'

	async def invoke(self, story_id, character_id, beats):
		dossier = await read_json(f'persona.{character_id}.json')
		story   = await read_json(f'story.{story_id}.json')
		digest  = await self.get_digest(character_id, beats)
		prompt  = self.fill(
			self.t,
			beats  = beats,
			digest = digest,
			** dossier
		)
		beat = await self.ask(prompt)
		beat['character_id'] = character_id
		return beat