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
	Authority,
	Duality,
	PodgornySquare,
	Personality,
	Subpersonality,
	CharacterSchema,
	StorySchema,
	LocationSchema
)
from client.operators import (
	Idea,
	Variations,

	Protogonist,
	Antagonist,

	Traumatologist,
	Dualist,
	Personalizer,
	Psychologist,
	Reader,
	Writer,
	Story,
	Locations
)

from lib import WordWield as ww


################################################################

if __name__ == '__main__':

	title         = 'Муха'
	genre         = 'Комедия'
	variations    = 11
	locations     = 3

	story = ww.invoke(
		Story,
		title      = title,
		genre      = genre,
		variations = variations,
		locations  = locations
	)

	protogonist = ww.invoke(
		Protogonist,
		story_id = story.id
	)
	antagonist = ww.invoke(
		Antagonist,
		story_id     = story.id,
		character_id = protogonist.id
	)

	print('names', protogonist.name, antagonist.name)
	print('IDEA:', idea)
