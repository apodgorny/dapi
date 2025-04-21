import json
from dapi.lib import Datum, OperatorDefinition
from typing import List, Dict, Any, Optional


################################################################

class main_input(Datum.Pydantic):
	depth: int
	topic: str
	idea: str = ""  # Add idea with default empty string

class main_output(Datum.Pydantic):
	text: str

class main(OperatorDefinition):
	def invoke(input):
		idea_result = idea({
			'topic' : input['topic']
		})
		print('IDEA:', idea_result['idea'])
		tree = recurse_plan({
			'topic'       : input['topic'],
			'idea'        : idea_result['idea'],
			'breadcrumbs' : [],

			'depth'       : input['depth'],
			'level'       : 0,
		})
		# Remove json dependency - print raw tree instead
		print("TREE STRUCTURE:", tree)
		return { 'text': idea_result['idea'] }


################################################################

class recurse_plan_input(Datum.Pydantic):
	topic       : str
	idea        : str
	breadcrumbs : List[str]

	level : int = 0
	depth : int

class recurse_plan_output(Datum.Pydantic):
	items : List[Dict[str, Any]]  # Using Dict instead of custom type to avoid schema issues

class recurse_plan(OperatorDefinition):
	def invoke(input):
		level       = input['level']
		depth       = input['depth']
		topic       = input['topic']
		idea        = input['idea']
		# Ensure breadcrumbs is a list
		print('type of breadcrumbs', type(input['breadcrumbs']))
		
		if not isinstance(input['breadcrumbs'], list):
			breadcrumbs = []
			print("WARNING: breadcrumbs is not a list - using empty list instead")
		else:
			breadcrumbs = input['breadcrumbs']

		title     = topic if len(breadcrumbs) == 0 else breadcrumbs[-1]
		bc_string = ('вот эту часть рассказа ' + '→'.join(breadcrumbs)) if breadcrumbs else 'весь текст рассказа'

		indent = '  ' * level
		print(indent, 'LEVEL', level, '→'.join(breadcrumbs or [topic]))

		children = []

		if level < depth:
			planner_result = planner({
				'topic'       : topic,
				'idea'        : idea,
				'breadcrumbs' : bc_string
			})

			print(indent, '  planner returned', planner_result)

			for subtitle in planner_result['titles']:
				child_result = recurse_plan({
					'level'       : level + 1,
					'depth'       : depth,
					'topic'       : topic,
					'idea'        : idea,
					'breadcrumbs' : breadcrumbs + [subtitle]
				})

				child_item = child_result['items'][0]
				print(indent, '  child item:', child_item)

				children.append(child_item)

		result = {
			'title': title,
			'sub'  : children
		}

		print(indent, 'END LEVEL', level, '→'.join(breadcrumbs or [topic]), 'with', len(children), 'children')

		return { 'items': [result] }


################################################################

class recurse_input(Datum.Pydantic):
	text  : str
	level : int = 0
	depth : int

class recurse_output(Datum.Pydantic):
	items : List[str]

class recurse(OperatorDefinition):
	def invoke(input):
		level   = input['level']
		depth   = input['depth']
		text    = input['text']
		results = []
		indent  = '  ' * level

		print(indent, 'BEGIN Level', level)
		if level < depth:
			diverged = diverge_story({
				'text': text
			})
			print(indent, 'Diverged', len(diverged['items']), 'items')
			for item in diverged['items']:
				recursed = recurse({
					'level' : level + 1,
					'depth' : depth,
					'text'  : item
				})
				print(indent, 'Recursed', len(recursed['items']), 'items')
				results += recursed['items']
		else:
			results += [text]
		print(indent, 'END Level', level, 'with', len(results), 'results')
		return { 'items': results }

################################################################

class diverge_story_input(Datum.Pydantic):
	text : str

class diverge_story_output(Datum.Pydantic):
	items : List[str]

class diverge_story(OperatorDefinition):
	code = '''
		Ты — писатель, пишущий художественную прозу на русском языке.
		Вот отрывок:
		"{{input.text}}"

		Развей его в **три части: завязка, накал и кульминационная развязка**.
		Верни их как список строк под ключом "items" в JSON:
		{
		  "items": ["...", "...", "..."]
		}

		Каждое продолжение должно быть:
		– литературным
		– логически связанным с исходной фразой
		– не длиннее 2–3 предложений
	'''

	interpreter = 'llm'
	config = {
		'model_id'    : 'ollama::gemma3:4b',
		'temperature' : 0.7
	}


################################################################

class idea_input(Datum.Pydantic):
	topic: str

class idea_output(Datum.Pydantic):
	idea : str

class idea(OperatorDefinition):
	code = '''
		Ты — шаман внимания, знающий как приворожить чувства словами, умеющий приклеить внимание слушателя виртуозно к своим словам.
		Ты получаешь чувство собственной значимости от того экстаза, который слушатель испытывает от путешествия с тобой в твоё повествование.
		А значит, и от тебя лично. Ты наслаждаешься этим. Я - твой любимый ученик, пишу рассказ и прошу помочь спланировать его.
		
		Мой рассказ на тему "{{input.topic}}". Придумай общую захватывающую идею и вырази её в 3-4 предложениях. Пожалуйста, оформи ТОЛЬКО идею в json formate.

		Спасибо.
	'''

	interpreter = 'llm'
	config = {
		'model_id'    : 'ollama::gemma3:4b',
		'temperature' : 0.7
	}


################################################################

class planner_input(Datum.Pydantic):
	topic       : str
	idea        : str
	breadcrumbs : str

class planner_output(Datum.Pydantic):
	titles : List[str]

class planner(OperatorDefinition):
	code = '''
		Ты — мастер планирования рассказов и книг.
		Tвоё мастерство - правильно озаглавить части книги, так, чтобы просто читая заголовки было понятно о чем будет глава.

		Идея рассказа на тему "{{input.topic}}" такая:

		"{{input.idea}}"

		Раздели {{input.breadcrumbs}} на 3 части и предоставь заголовки.
		Сложи их в JSON:

		{
		  "titles" : ["...", "...", "..." ]
		}

		Kaждый заголовок ("chapter") должен быть 5-7 слов.
		Рассказ должен получиться захватывающим благодаря твоей точности передачи смысла через заголовки!
		Спасибо.
	'''

	interpreter = 'llm'
	config = {
		'model_id'    : 'ollama::gemma3:4b',
		'temperature' : 0.7
	}


################################################################
class Process:
	entry = main
