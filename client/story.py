import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.lib.client import Client
from dapi.lib.datum    import Datum

##########################################################################################

class recurse_input(Datum.Pydantic):
	phrase: str
	level : int

class recurse_output(Datum.Pydantic):
	items: list[str]

class diverge_story_input(Datum.Pydantic):
	phrase: str

class diverge_story_output(Datum.Pydantic):
	stories: list[str]

Client.create_type('recurse_input',         recurse_input)
Client.create_type('recurse_output',        recurse_output)
Client.create_type('diverge_story_input',   diverge_story_input)
Client.create_type('diverge_story_output',  diverge_story_output)

##########################################################################################

fragment_code = '''
Ты — писатель, пишущий художественную прозу на русском языке.
Вот отрывок:
"{{input.phrase}}"

Развей его в **три части: вступление, основную часть и завершение**.
Верни их как список строк под ключом "stories" в JSON:
{
  "stories": ["...", "...", "..."]
}

Каждое продолжение должно быть:
– литературным
– логически связанным с исходной фразой
– не длиннее 2–3 предложений
'''

Client.create_operator(
	name        = 'diverge_story',
	input_type  = 'diverge_story_input',
	output_type = 'diverge_story_output',
	code        = fragment_code,
	interpreter = 'llm',
	config      = {
		'model_id'   : 'ollama::gemma3:4b',
		'temperature': 0.7
	}
)

##########################################################################################

recurse_code = '''
def recurse(input):
	n       = input['level']
	text    = input['phrase']
	sources = []

	for tag in ['начало', 'развитие', 'кульминация']:
		response = diverge_story({'phrase': text + ' — ' + tag})
		for story in response['stories']:
			sources += [story]

	if n > 0:
		results = []
		for source in sources:
			diverged = recurse({'level': n - 1, 'phrase': source})
			for s in diverged:
				results += [s]
		return { 'items': results }

	return { 'items': sources }
'''

Client.create_operator(
	name        = 'recurse',
	input_type  = 'recurse_input',
	output_type = 'recurse_output',
	code        = recurse_code,
	interpreter = 'python'
)

##########################################################################################

input_data = {
	'phrase': 'Ветер вёл его через мрак',
	'depth' : 1
}

print('input:', input_data)
result = Client.invoke('recurse', {
	'level' : input_data['depth'],
	'phrase': input_data['phrase']
})
print('\n🎞️ Результат:\n')
print(result)
