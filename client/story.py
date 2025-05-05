import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic             import BaseModel
from typing               import List

from wordwield.wordwield  import Operator, WordWield as ww


################################################################

class DivergeStory(Operator):

	class InputType(BaseModel):
		text : str

	class OutputType(BaseModel):
		items : List[str]

	prompt = '''
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

	def invoke(self, text):
		return self.ask(text=text)


################################################################

class Idea(Operator):

	class InputType(BaseModel):
		topic : str

	class OutputType(BaseModel):
		idea : str

	prompt = '''
		Ты — шаман внимания, знающий как приворожить чувства словами, умеющий приклеить внимание слушателя виртуозно к своим словам.
		Ты получаешь чувство собственной значимости от того экстаза, который слушатель испытывает от путешествия с тобой в твоё повествование.
		А значит, и от тебя лично. Ты наслаждаешься этим. Я — твой любимый ученик, пишу рассказ и прошу помочь спланировать его.
		
		Мой рассказ на тему "{{topic}}". Придумай общую захватывающую идею и вырази её в 3–4 предложениях. Пожалуйста, оформи ТОЛЬКО идею в JSON-формате.
		
		Спасибо.
	'''

	def invoke(self, topic):
		return self.ask(topic=topic)


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

	prompt = '''
		Ты — мастер планирования рассказов и книг.
		Tвоё мастерство — правильно озаглавить части книги, так, чтобы просто читая заголовки было понятно, о чём будет глава.

		Идея рассказа на тему "{{topic}}" такая:

		"{{idea}}"

		Сейчас работаем над частью {{item}} в разделе {{breadcrumbs}}.
		Раздели её на {{spread}} части и предоставь заголовки.
		Сложи их в JSON:

		{
		  "items" : ["...", "...", "..." ]
		}

		Kaждый заголовок должен быть 5–7 слов.
		Рассказ должен получиться захватывающим благодаря твоей точности передачи смысла через заголовки!
		Спасибо.
	'''

	def invoke(
		self,
		topic       : str,
		idea        : str,
		item        : str,
		spread      : str,
		breadcrumbs : str
	):
		return self.ask(
			topic       = topic,
			idea        = idea,
			item        = item,
			spread      = spread,
			breadcrumbs = breadcrumbs
		)


################################################################

class Story(Operator):

	class InputType(BaseModel):
		topic  : str
		depth  : int
		spread : int

	class OutputType(BaseModel):
		root : dict

	async def invoke(self, topic, depth, spread):
		idea_text = await idea(topic=topic)

		planner_input = {
			'topic' : topic,
			'idea'  : idea_text,
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

def display_tree(node, indent=0):
	'''Recursively prints a tree based on 'in' fields.'''
	if not node:
		return
	print('    ' * indent + str(node.get('in', '')))
	for child in node.get('out', []):
		display_tree(child, indent + 1)


################################################################

if __name__ == '__main__':

	def main():
		ww.create_operator(DivergeStory)
		ww.create_operator(Idea)
		ww.create_operator(Planner)
		ww.create_operator(Story)

		result = ww.invoke('story',
			topic  = 'Ромашка',
			depth  = 3,
			spread = 3
		)

		display_tree(result['output']['root'])

	main()
