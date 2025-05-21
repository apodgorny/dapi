from lib import (
	O,
	Operator,
	Agent,
	Spinner
)
from client.schemas import (
	BeatSchema
)
from dapi.schemas import (
	SpinnerCriteriaSchema,
	SpinnerStructureSchema
)

class Chel(Spinner):
	class InputType(O):
		beats        : list[str]
		character_id : str
		opponent_id  : str
		description  : str
		purpose      : str

	class OutputType(O):
		beat : BeatSchema

	class Templates:
		generate_spin_criteria = '''
			Ты — помощник-драматург. Проанализируй диалог и заполни внутреннее состояние персонажа и оппонента по критериям.

			# Персонаж:
			{{character_id}}
			{{description}}
			# Цель персонажа
			{{purpose}}

			# Оппонент: {{opponent_id}}

			# Диалог:
			{{beats_text}}

			Заполни все поля схемы
		'''

		generate_spin_structure = '''
			Ты - {{character_id}}
			# Твоё описание
			{{description}}
			# Цель персонажа
			{{purpose}}

			# Оппонент: {{opponent_id}}

			# КРИТЕРИИ
			{{spin_criteria}}

			# Диалог:
			{{beats_text}}
			# Конец диалога

			Ты пытаешься решить, что ответить на последнюю фразу диалога:
			{{last_phrase}}

			Но учитываешь свои чувства в течение всего разговора.
			Какие вопросы ты задашь себе чтобы лучше раскрыть суть происходящего,
			замыслы и состояние оппонента и свою собственную расположенность к действию.

			**Формат:**
			Ключ — короткое название этапа мышления.  
			Значение — КОММАНДА себе. Что ты должен(на) спросить себя?

		'''

		spin_in = '''
			Ты — {{description}}.
			Твоя задача — {{purpose}}.
			
			Вот весь ваш предыдущий диалог:
			{{beats_text}}

			Последняя фраза диалога:
			{{last_phrase}}
		'''

		spins = {
			'Твоё наблюдение' : '''
				Что буквально сказал собеседник в своей последней реплике? Перепиши её одной строкой в своём понимании.
			''',
			'Твоя ориентировка' : '''
				Какие эмоции, мотивы или внутреннее состояние можно считать явными по этой фразе? Не анализируй всю беседу — только эту реплику.
				Не повторяй фразу, но опиши, что ты из неё понял(а)
			''',
			'Твоё решение' : '''
				Какое твоё главное намерение после такого ответа? Нужно ли сменить тактику: продолжить напор, смягчить флирт, перевести в шутку, отступить? Обоснуй в одно предложение.
			''',
			'Твои варианты поведения' : '''
				Предложи несколько вариантов фраз, которые ты хочешь сказать, или которые приблизят тебя к твоей цели.
				Если уместно, добавь короткое физическое действие (одной строкой).
			'''
		}

		spin_out = '''
			На основе "Твои варианты поведения", напиши только:
			- Конкретную реплику (speech)
			- Короткое действие (action)
			Используй окончания слов соответствующие полу
			Без пояснений и мыслей!
		'''

	async def invoke(self, beats: list[str], character_id, opponent_id, description, purpose):
		self.log('RESET', clear=True)
		beats_text  = '\n'.join(beats)
		last_phrase = beats[-1] if beats else ''

		# structure = await self.generate_spin_structure(
		# 	character_id = character_id,
		# 	opponent_id  = opponent_id,
		# 	description  = description,
		# 	purpose      = purpose,
		# 	beats        = beats,
		# 	beats_text   = beats_text,
		# 	last_phrase  = last_phrase,
		# )

		return await self.spin(
			character_id = character_id,
			opponent_id  = opponent_id,
			description  = description,
			purpose      = purpose,
			beats        = beats,
			beats_text   = beats_text,
			last_phrase  = last_phrase,
		)
