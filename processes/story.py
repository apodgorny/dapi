from dapi.lib import Datum, OperatorDefinition


################################################################

class recurse_input(Datum.Pydantic):
	text  : str
	level : int = 0
	depth : int

class recurse_output(Datum.Pydantic):
	items : list[str]

class diverge_story_input(Datum.Pydantic):
	text : str

class diverge_story_output(Datum.Pydantic):
	items : list[str]


################################################################

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

class diverge_story(OperatorDefinition):
	code = '''
		Ты — писатель, пишущий художественную прозу на русском языке.
		Вот отрывок:
		"{{input.text}}"

		Развей его в **три части: вступление, основную часть и завершение**.
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

class Process:
	entry = recurse
