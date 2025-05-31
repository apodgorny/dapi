# from pydantic             import BaseModel
# from typing               import List, Dict, Any

# from lib import (
# 	O,
# 	Operator,
# 	Agent,
# 	Expert,
# )


# class Planner(Expert):

# 	t_current_empty = '''
# 		Сейчас только начинаем разбивать идею на заголовки.
# 	'''

# 	t_current = '''
# 		Сейчас работаем над частью {{crumbs}}.
# 	'''

# 	t_previous_empty = '''
# 		Это начало планировки глав. Заложи в названия глав "завязку", "развитие" и "развязку" сюжета.
# 	'''

# 	t_previous = '''
# 		Вот главы, которые шли до этой части:
# 		{{previous_titles}}
# 	'''

# 	t_correction = '''
# 		Главы обязательно должны начинаться с фраз "Завязка сюжета" или "Развитие сюжета" или "Развязка сюжета".
# 	'''

# 	t_capitalize = '''
# 		Ты — мастер планирования рассказов и книг.
# 		Tвоё мастерство — правильно озаглавить части книги, так, чтобы просто читая заголовки было понятно, о чём будет глава.

# 		Идея рассказа на тему "{{topic}}" такая:

# 		"{{idea}}"
		
# 		{{current_state}}
# 		{{previous_titles}}

# 		Раздели часть "{{subtitle}}" на {{spread}} логично следующих заголовка.
# 		{{correction}}
# 		Сложи их в JSON:

# 		{
# 		  "items" : [{title: ...}, {title: ...}, ... ]
# 		}

# 		Kaждый заголовок должен быть 5–7 слов.
# 		Рассказ должен получиться захватывающим благодаря твоей точности передачи смысла через заголовки!
# 		Спасибо.
# 	'''

# 	async def _capitalize(self, state, data, h_ctx, v_ctx, c_ctx, initial=False):
# 		t_current = self.t_current_empty if not v_ctx else self.t_current
# 		current_state = self.fill(
# 			t_current,
# 			subtitle = data['title'],
# 			crumbs   = '->'.join(['"' +t['title'] + '"' for t in v_ctx])
# 		)

# 		t_previous = self.t_previous_empty if not h_ctx else self.t_previous
# 		previous_titles = ' - ' + '\n - '.join(['"' +t['title'] + '"' for t in h_ctx])
# 		previous_titles = self.fill(
# 			t_previous,
# 			previous_titles = previous_titles
# 		)

# 		prompt = self.fill(
# 			self.t_capitalize,
# 			topic           = c_ctx['topic'],
# 			idea            = c_ctx['idea'],
# 			spread          = c_ctx['spread'],
# 			subtitle        = data['title'],
# 			current_state   = current_state,
# 			previous_titles = previous_titles,
# 			correction      = self.t_correction if initial else ''
# 		)
# 		print(prompt)
# 		return await self.ask(prompt)

# 	t_current_write_empty = '''
# 		Ты пишешь самое начало книги. Это вступление.
# 	'''

# 	t_current_write = '''
# 		Напиши следующую главу: {{crumbs}}.
# 	'''

# 	t_previous_write_empty = '''
# 	'''

# 	t_previous_write = '''
# 		Вот текст книги до сих пор:
# 		BEGIN TEXT ---------------------------
# 		{{previous_text}}
# 		END TEXT ---------------------------
# 	'''

# 	t_write = '''
# 		Ты талантливый писатель.
# 		Ты пишешь книгу "{{topic}}".
# 		Её сюжет: "{{idea}}".
# 		{{previous_text}}
# 		{{current_state}}
# 		Глава должна быть 5 предложений и логически следовать из сюжета.
# 		Сложи в json вот так:
# 		{
# 		  "items" : [{text: "<глава здесь>"}]
# 		}
# 	'''

# 	async def _write(self, state, data, h_ctx, v_ctx, c_ctx):
# 		t_current = self.t_current_write_empty if not v_ctx else self.t_current_write
# 		current_state = self.fill(
# 			t_current,
# 			subtitle = data['title'],
# 			crumbs   = '->'.join(['"' +t['title'] + '"' for t in v_ctx])
# 		)

# 		t_previous = self.t_previous_write_empty if not h_ctx[-2:] else self.t_previous_write
# 		previous_text = '\n'.join([t['text'] for t in h_ctx[-2:]])
# 		previous_text = self.fill(
# 			t_previous,
# 			previous_text = previous_text
# 		)

# 		prompt = self.fill(
# 			self.t_write,
# 			topic           = c_ctx['topic'],
# 			idea            = c_ctx['idea'],
# 			current_state   = current_state,
# 			previous_text = previous_text,
# 		)
# 		print(prompt)
# 		return await self.ask(prompt)

# 	async def invoke(self, state, data, h_ctx, v_ctx, c_ctx):
# 		if state == 'one':
# 			return await self._capitalize(state, data, h_ctx, v_ctx, c_ctx, initial=True)
# 		elif state == 'two':
# 			return await self._capitalize(state, data, h_ctx, v_ctx, c_ctx, initial=False)
# 		elif state == 'three':
# 			return await self._write(state, data, h_ctx, v_ctx, c_ctx)

