from lib import (
	O,
	Agent
)


class Evolve(Agent):
	class InputType(O):
		text      : str
		summarize : bool
		clear     : bool

	class OutputType(O):
		text : str

	class QuestionType(O):
		question: str

	class Templates:
		question = '''
			Задай самый вероятный вопрос о тексте.
			---------------
			ТЕХТ:
			{{text}}
			---------------
		'''

		answer = '''
			Эволюционируй мыслью и ответь на вопрос о тексте.
			---------------
			ТЕХТ:
			{{text}}
			---------------
			ВОПРОС:
			"{{question}}"
			---------------
			!!НЕ ПОВТОРЯЙ ТЕКСТ ДОСЛОВНО!!
		'''

		summary = '''
			Суммаризируй в одно предложение текст:
			---------------
			ТЕХТ:
			{{text}}
			---------------
		'''

	async def invoke(self, text, summarize=False, clear=False):
		hr = '\n-------------------\n'
		self.log(text, hr, name='custom', clear=clear)
		question = await self.ask(
			self.fill(
				self.Templates.question,
				text = text
			), 
			self.QuestionType
		)
		self.log(question, hr, name='custom')
		answer = await self.ask(
			self.fill(
				self.Templates.answer,
				text     = text,
				question = question
			)
		)
		if summarize:
			self.log(answer, hr, name='custom')
			answer = await self.ask(
				self.fill(
					self.Templates.summary,
					text = text + '\n' + answer,
				)
			)
		return answer