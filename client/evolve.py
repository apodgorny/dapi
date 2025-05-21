# Add Python's sys.path manipulation to ensure imports work correctly
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic             import BaseModel
from typing               import List, Dict, Any

DATA_DIR = os.environ.get('DATA_DIR')

from client.operators import (
	Evolve,
	Evolve1
)
from lib import WordWield as ww, O


class TextType(O):
	text: str

################################################################

def handle_input(text, evolutions=1):
	for n in range(evolutions):
		evolved_text = ww.invoke(
			Evolve1,
			text      = text,
			summarize = False,
			clear     = (n == 0),
		)
		if evolved_text == text:
			break
		text = evolved_text
	return text 

evolutions = 2

# if __name__ == '__main__':
# 	while True:
# 		user_input = input('> ')
# 		if user_input.strip().lower() == 'exit':
# 			print('Goodbye!')
# 			break
# 		evolved_text = handle_input(user_input, evolutions)
# 		print('> ' + evolved_text)
text = 'У попа была собака, он её любил. Она съела кусок мяса - он её убил.'
handle_input(text, evolutions)
