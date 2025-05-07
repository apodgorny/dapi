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
	Reader,
	Writer
)

from lib import WordWield as ww

PROJECT_PATH = os.environ.get('PROJECT_PATH')
DATA_DIR     = os.environ.get('DATA_DIR')
DATA_PATH    = os.path.join(PROJECT_PATH, DATA_DIR)


################################################################

if __name__ == '__main__':

	initial_topic = 'Муха'
	genre         = 'Комедия'
	n_questions   = 3

	topic = ww.invoke(
		Interpretations,
		title  = initial_topic,
		theme  = genre,
		spread = 10
	)
	idea = ww.invoke(
		Idea,
		topic = topic,
		theme = genre
	)
	questions = ww.invoke(
		Reader,
		idea   = idea,
		spread = n_questions
	)
	answers = ww.invoke(
		Writer,
		title     = topic,
		genre     = genre,
		idea      = idea,
		questions = questions,
		spread    = 3
	)

	print('IDEA:', idea)

	for n in range(n_questions):
		print('='*30)
		print('QUESTION:', questions[n])
		print('ANSWER:', answers[n])

	
	# questions = ww.invoke(Reader, idea=idea)
