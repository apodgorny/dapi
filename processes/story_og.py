# Add Python's sys.path manipulation to ensure imports work correctly
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic             import BaseModel
from typing               import List, Dict, Any

# Use absolute imports to avoid issues when running script directly
from processes.schemas import (
	Persona,
	Trauma,
	Authority,
	Duality,
	PodgornySquare
)
from processes.agents import (
	Idea,
	Interpretations,

	Character,
	Protogonist,
	Antagonist,

	Traumatologist,
	Dualist,
	Psychologist,
)

from wordwield.wordwield  import (
	Agent,
	WordWield as ww
)


################################################################

if __name__ == '__main__':

	ww.init()
	initial_topic = 'Ромашка'
	theme         = 'Комедия'
	topic         = ww.invoke(Interpretations, title=initial_topic, theme=theme, spread=10)
	idea          = ww.invoke(Idea,            topic=topic, theme=theme)
	protogonist   = ww.invoke(Protogonist,     title=topic, idea=idea, theme=theme)
	# antagonist    = ww.invoke(Antagonist,      title=topic, idea=idea, theme=theme, character=protogonist)
	traumas, dualities = ww.invoke(Psychologist,    complexity=1, persona=protogonist)

	print('title',      initial_topic)
	print('theme',      theme)
	print('topic',      topic)
	print('idea',       idea)
	print('character',  protogonist)
	print('traumas',    traumas)
	print('dualities',  dualities)
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
