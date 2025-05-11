import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic             import BaseModel
from typing               import List

from lib import (
	O,
	Agent
)
from client.schemas import (
	PersonaSchema,
	Personality,
	Trauma,
	Duality,
	Subpersonality,
	CharacterSchema
)


class Traumatologist(Agent):
	class InputType(O):
		persona     : PersonaSchema
		complexity  : int

	class OutputType(O):
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
			''',

		'cta_one'  : 'Опиши главную травму детства этого человека',
		'cta_many' : 'Опиши список {{complexity}} главных травм детства этого человека.'
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
		return prompt

	async def invoke(self, persona, complexity):
		prompt = self.get_traumas(persona, complexity)
		return await self.ask(prompt)

#####################################################################

class Dualist(Agent):
	class InputType(O):
		persona  : PersonaSchema
		trauma   : Trauma

	class OutputType(O):
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
				(ВАЖНО: не оставляй поля пустыми):
			'''
	}

	async def invoke(self, persona, trauma):
		prompt = self.fill(
			self.t['main'],
			persona = persona,
			trauma  = trauma
		)
		return await self.ask(prompt)


class Personalizer(Agent):

	class InputType(O):
		dualities : list[Duality]

	class OutputType(O):
		personality: Personality

	t = {
		'main':
			'''
				Дуальности:
				{{dualities}}

				Ты — психолог, чья задача — формировать субличности, объединяя стороны из вышеперечисленных дуальностей
				в целостные, атомарные и внутренне согласованные роли.

				Вот твоя основная цель: **создать субличности**, в которых **каждая сторона усиливает другую**,а не противоречит ей.
				Субличность — это локальный минимум: точка внутренней устойчивости,
				в которую естественным образом "скатывается" точка сборки при определённых условиях.

				У тебя есть список дуальностей. Каждая дуальность содержит две стороны: `yin` и `yang`. У каждой стороны есть:
				- `name` — имя стороны
				- `authority` — фигура, на которой она основана
				- `judgement_to_self`, `judgement_to_opposite` — внутренние осуждения
				- `square` — коэффициенты вины и активности
				- ресурсная и мотивационная структура

				Принципы формирования субличностей:

				1. **Ценности и убеждения** — стороны в одной субличности должны иметь схожие или взаимодополняющие взгляды на мир.
				2. **Эмоциональный фон** — эмоции, связанные со сторонами, не должны конфликтовать.
				3. **Цель и мотивация** — мотивации должны быть направлены в одну сторону, не блокируя друг друга.
				4. **Стратегии поведения** — поведенческие паттерны сторон должны быть совместимыми.
				5. **Ресурсная база** — стороны должны опираться на совместимые ресурсы.
				6. **Внутренняя оценка** — ни одна сторона не должна осуждать другую в рамках одной субличности.
				7. **Без конфликта авторитетов** — авторитеты сторон не должны находиться в противоборстве.

				Правила:

				- Не используй обе стороны из одной дуальности в одной субличности.
				- Каждая сторона может входить только в одну субличность.
				- Если сторона не находит себе пары — оформи её как отдельную субличность.
				- Дай каждой субличности метафоричное или архетипическое имя (например: «Внутренний Творец», «Наблюдатель Боли», «Тихий Архитектор»).
			'''
	}

	async def invoke(self, dualities):
		prompt = self.fill(
			self.t['main'],
			dualities = dualities
		)
		return await self.ask(prompt)


class Psychologist(Agent):
	class InputType(O):
		persona     : PersonaSchema
		complexity  : int

	class OutputType(O):
		character: CharacterSchema

	async def invoke(self, persona, complexity):
		dualities = []
		traumas = await traumatologist(persona=persona, complexity=complexity)

		for trauma in traumas:
			duality = await dualist(persona=persona, trauma=trauma)
			dualities.append(duality)

		personality = await personalizer(dualities=dualities)

		return CharacterSchema(
			persona     = persona,
			personality = personality,
			traumas     = traumas,
			dualities   = dualities
		)