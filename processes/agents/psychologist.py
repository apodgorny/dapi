import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic             import BaseModel
from typing               import List

from wordwield.wordwield  import Agent, WordWield as ww
from processes.schemas    import Persona, Personality, Trauma, Duality


class Traumatologist(Agent):
	class InputType(BaseModel):
		persona     : Persona
		complexity  : int

	class OutputType(BaseModel):
		traumas: list[Trauma]

	t = {
		'main':
			'''
				Ты — опытный психолог, умеющий распознавать глубинные структуры личности по краткому описанию человека.
				Вот описание человека:
				{{persona}}.
				Ты провел детальное исследование и теперь полностью уверен в результатах.

				{{cta}}
				Используй ассертивные, краткие и однозначные утверждения.
				Сложи травматические данные в JSON (ВАЖНО: не оставляй поля пустыми):
				
			''' + '{ traumas: [' + Trauma.prompt() + ', ... ] }',
		'cta_one':
			'''Опиши главную травму детства этого человека''',
		'cta_many':
			'''Опиши список {{complexity}} главных травм детства этого человека.'''
	}

	def get_traumas(self, persona, complexity):
		cta_key = 'cta_one' if complexity <= 1 else 'cta_many'
		cta = self.fill(
			self.t[cta_key],
			complexity = complexity
		)
		prompt = self.fill(
			self.t['main'],
			persona = persona,
			cta     = cta
		)
		print(prompt)
		return prompt

	async def invoke(self, persona, complexity):
		prompt = self.get_traumas(persona, complexity)
		return await self.ask(prompt)

#####################################################################

class Dualist(Agent):
	class InputType(BaseModel):
		persona  : Persona
		trauma   : Trauma

	class OutputType(BaseModel):
		duality: Duality

	t = {
		'main':
			'''
				Ты — опытный психолог, специализирующийся на распознании субличностей и дуальностей мышления.
				Вот описание человека:
				{{persona}}.
				
				А вот травма с которую ты исследуешь.
				{{trauma}}

				Ты провёл опрос и теперь точно знаешь всё о дуальности сопутствующей этой травме.
				Опиши дуальность.
				Используй ассертивные, краткие и однозначные утверждения.
				Сложи данные дуальности в JSON (ВАЖНО: не оставляй поля пустыми):
				
			''' + '{ duality: ' + Duality.prompt() + ' }',
	}

	async def invoke(self, persona, trauma):
		prompt = self.fill(
			self.t['main'],
			persona = persona,
			trauma  = trauma
		)
		return await self.ask(prompt)


class Psychologist(Agent):
	class InputType(BaseModel):
		persona     : Persona
		complexity  : int

	class OutputType(BaseModel):
		traumas   : list[Trauma]
		dualities : list[Duality]

	async def invoke(self, persona, complexity):
		dualities = []
		traumas = await traumatologist(persona=persona, complexity=complexity)

		for trauma in traumas:
			duality = await dualist(persona=persona, trauma=trauma)
			dualities.append(duality)

		return traumas, dualities