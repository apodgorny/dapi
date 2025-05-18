# Add Python's sys.path manipulation to ensure imports work correctly
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic             import BaseModel
from typing               import List, Dict, Any

DATA_DIR = os.environ.get('DATA_DIR')

# from lib.debug import debugpy

# Use absolute imports to avoid issues when running script directly
from client.schemas import (
	PersonaSchema,
	Trauma,
	TraumaAttributes,
	TraumaComponents,
	TraumaCoping,
	Side,
	Resource,
	Authority,
	Duality,
	PodgornySquare,
	Personality,
	Subpersonality,
	CharacterSchema,
	StorySchema,
	LocationSchema,
	RelationsSchema,
	RelationSchema,
	BeatSchema,
	DirectorBeatSchema
)
from client.operators import (
	Idea,
	Variations,

	Protogonist,
	Antagonist,
	Character,
	Director,

	Traumatologist,
	Dualist,
	Personalizer,
	Psychologist,
	Reader,
	Writer,
	Story,
	Locations,
	Relations,
	Stage,
	Chel
)

from lib import WordWield as ww


################################################################

beats = []

def handle_input(question, beats):
	user_beat = BeatSchema(
		character_id = 'Молодой человек',
		speech       = question,
		action       = ''
	)
	beats.append(user_beat)
	chel_beat = ww.invoke(
		Chel,
		beats = '\n'.join([b.prompt() for b in beats])
	)
	beats.append(chel_beat)
	return chel_beat 


if __name__ == '__main__':
	while True:
		question = input('> ')
		if question.strip().lower() == 'exit':
			print('Goodbye!')
			break
		beat = handle_input(question, beats)
		print('> ' + beat.speech + f'({beat.action})')
