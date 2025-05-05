# Add Python's sys.path manipulation to ensure imports work correctly
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic             import BaseModel
from typing               import List, Dict, Any

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
from client.agents import (
	Idea,
	Interpretations,

	Protogonist,
	Antagonist,

	Traumatologist,
	Dualist,
	Personalizer,
	Psychologist,
)

from wordwield.wordwield  import (
	Agent,
	WordWield as ww
)


################################################################

if __name__ == '__main__':

	ww.init()
	initial_topic = 'Муха'
	theme         = 'Комедия'
	topic         = ww.invoke(Interpretations, title=initial_topic, theme=theme, spread=10)
	idea          = ww.invoke(Idea,            topic=topic, theme=theme)
	protogonist_persona    = ww.invoke(Protogonist, title=topic, idea=idea, theme=theme)
	print('protogonist_persona', type(protogonist_persona), protogonist_persona)
	# antagonist    = ww.invoke(Antagonist,      title=topic, idea=idea, theme=theme, character=protogonist)
	protogonist_character  = ww.invoke(Psychologist, complexity=1, persona=protogonist_persona)

	print('title',       initial_topic)
	print('theme',       theme)
	print('topic',       topic)
	print('idea',        idea)

	protogonist_character.to_disk('/Users/alexander/my/dapi/client/data')
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
