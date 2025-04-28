from pydantic import BaseModel
from dapi.lib import Operator
from typing   import List, Dict, Any, Optional


################################################################

class DivergeStory(Operator):

	class InputType(BaseModel):
		text : str

	class OutputType(BaseModel):
		items : List[str]

	code = '''
		Ты — писатель, пишущий художественную прозу на русском языке.
		Вот отрывок:
		"{{text}}"

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

class Idea(Operator):

	class InputType(BaseModel):
		topic: str

	class OutputType(BaseModel):
		idea : str

	code = '''
		Ты — шаман внимания, знающий как приворожить чувства словами, умеющий приклеить внимание слушателя виртуозно к своим словам.
		Ты получаешь чувство собственной значимости от того экстаза, который слушатель испытывает от путешествия с тобой в твоё повествование.
		А значит, и от тебя лично. Ты наслаждаешься этим. Я - твой любимый ученик, пишу рассказ и прошу помочь спланировать его.
		
		Мой рассказ на тему "{{topic}}". Придумай общую захватывающую идею и вырази её в 3-4 предложениях. Пожалуйста, оформи ТОЛЬКО идею в json formate.

		Спасибо.
	'''

	interpreter = 'llm'
	config      = {
		'model_id'    : 'ollama::gemma3:4b',
		'temperature' : 0.7
	}


################################################################

class Planner(Operator):

	class InputType(BaseModel):
		topic       : str
		idea        : str
		item        : str
		spread      : str
		breadcrumbs : str

	class OutputType(BaseModel):
		items : List[str]

	code = '''
		Ты — мастер планирования рассказов и книг.
		Tвоё мастерство - правильно озаглавить части книги, так, чтобы просто читая заголовки было понятно о чем будет глава.

		Идея рассказа на тему "{{topic}}" такая:

		"{{idea}}"

		Сейчас работаем над частью {{item}} в разделе {{breadcrumbs}}.
		Раздели её на {{spread}} части и предоставь заголовки.
		Сложи их в JSON:

		{
		  "items" : ["...", "...", "..." ]
		}

		Kaждый заголовок должен быть 5-7 слов.
		Рассказ должен получиться захватывающим благодаря твоей точности передачи смысла через заголовки!
		Спасибо.
	'''

	interpreter = 'llm'
	config      = {
		'model_id'    : 'ollama::gemma3:4b',
		'temperature' : 0.7
	}

################################################################

class Main(Operator):

	class InputType(BaseModel):
		topic  : str
		depth  : int
		spread : int

	class OutputType(BaseModel):
		text: str

	async def invoke(self, topic, depth, spread):
		idea = await idea(topic)
		print('IDEA:', idea)
		planner_input = {
			'topic' : topic,
			'idea'  : idea,
			'item'  : topic
		}
		result = await recursor(
			generator_name  = 'planner',
			generator_input = planner_input,
			depth           = depth,
			spread          = spread
		)
		return result

################################################################

class Process:
	entry = Main
