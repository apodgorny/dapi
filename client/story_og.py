# Add Python's sys.path manipulation to ensure imports work correctly
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic             import BaseModel
from typing               import List, Dict, Any

DATA_DIR = os.environ.get('DATA_DIR')

# from lib.debug import debugpy

# Use absolute imports to avoid issues when running script directly
from client.schemas import (
	Persona,
	Trauma,
	Authority,
	Duality,
	PodgornySquare,
	Personality,
	Subpersonality,
	Character
)
from client.operators import (
	Idea,
	Interpretations,

	Protogonist,
	Antagonist,

	Traumatologist,
	Dualist,
	Personalizer,
	Psychologist,
)

from lib import WordWield as ww

PROJECT_PATH = os.environ.get('PROJECT_PATH')
DATA_DIR     = os.environ.get('DATA_DIR')
DATA_PATH    = os.path.join(PROJECT_PATH, DATA_DIR)


################################################################

if __name__ == '__main__':

	ww.init()
	print('done')
	initial_topic = 'Муха'
	theme         = 'Комедия'
	topic         = ww.invoke(Interpretations, title=initial_topic, theme=theme, spread=10)
	idea          = ww.invoke(Idea,            topic=topic, theme=theme)
	protogonist_persona    = ww.invoke(Protogonist, title=topic, idea=idea, theme=theme)
	print('protogonist_persona', type(protogonist_persona), protogonist_persona)
	# antagonist    = ww.invoke(Antagonist,      title=topic, idea=idea, theme=theme, character=protogonist)
	# protogonist_character  = ww.invoke(Psychologist, complexity=1, persona=protogonist_persona)

	print('title', initial_topic)
	print('theme', theme)
	print('topic', topic)
	print('idea',  idea)

	# protogonist_character.to_disk(os.path.join(DATA_PATH, 'protogonist.json'))
	print(protogonist_character)
	# print('antagonist', antagonist)
	
	# sg = StateGrid(
	# 	state_names   = ['one', 'two', 'three', 'four'],
	# 	operator_name = 'planner',
	# 	common        = {
	# 		'topic'  : topic,
	# 		'idea'   : idea,
	# 		'spread' : 3
	# 	}
	# )
	# sg.invoke(
	# 	title = topic
	# )

	# book = '\n\n'.join(sg['four'].values('text'))

	# with open(f'/Users/alexander/my/dapi/output/{initial_topic}.txt', 'w') as f:
	# 	f.write(book)
