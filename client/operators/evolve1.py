from lib import (
	O,
	Agent
)


class Evolve1(Agent):
	class InputType(O):
		text      : str
		summarize : bool
		clear     : bool

	class OutputType(O):
		text : str

	class Templates:
		t = '''
			Перепиши этот текст в текст длиной примерно {{size}} букв.
			---------------
			ТЕХТ:
			{{text}}
			---------------
		'''

	async def invoke(self, text, summarize=False, clear=False):
		hr = '\n-------------------\n'
		self.log(text, hr, name='custom', clear=clear)
		text = await self.ask(
			self.fill(
				self.Templates.t,
				text = text,
				size = len(text) * 3
			), 
		)
		self.log(text, hr, name='custom')
		text = await self.ask(
			self.fill(
				self.Templates.t,
				text = text,
				size = len(text) * 3
			)
		)
		self.log(text, hr, name='custom')
		text = await self.ask(
			self.fill(
				self.Templates.t,
				text = text,
				size = int(len(text) / 3)
			)
		)
		self.log(text, hr, name='custom')
		text = await self.ask(
			self.fill(
				self.Templates.t,
				text = text,
				size = int(len(text) / 3)
			)
		)
		return text