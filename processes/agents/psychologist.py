import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic             import BaseModel
from typing               import List

from wordwield.wordwield  import Agent, WordWield as ww
from processes.schemas    import Persona, Personality, Trauma


class Psychologist(Agent):
	class InputType(BaseModel):
		persona     : Persona
		complexity  : int

	class OutputType(BaseModel):
		traumas: list[Trauma]

	t_get_traumas_cta_one = '''
		Опиши главную травму детства этого человека и сложи её данные в JSON
	'''

	t_get_traumas_cta_many = '''
		Опиши список {{complexity}} главных травм детства этого человека.
		Сложи их в JSON: 
	'''

	t_get_traumas = '''
		Ты — опытный психолог, умеющий распознавать глубинные структуры личности по краткому описанию человека.
		Вот описание человека:
		{{persona}}.

		{{get_traumas_cta}}
		{ traumas: [
	''' + Trauma.prompt() + ', ... ]}'

	def get_traumas(self, persona, complexity):
		t_get_traumas_cta = self.t_get_traumas_cta_one if complexity <= 1 else self.t_get_traumas_cta_many
		get_traumas_cta = self.fill(
			t_get_traumas_cta,
			complexity = complexity
		)
		prompt = self.fill(
			self.t_get_traumas,
			persona         = persona,
			get_traumas_cta = get_traumas_cta
		)
		print(prompt)
		return prompt

	async def invoke(self, persona, complexity):
		prompt = self.get_traumas(persona, complexity)
		return await self.ask(prompt)