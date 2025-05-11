import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib             import O
from .psychology     import Personality, Trauma, Duality
from .persona_schema import PersonaSchema


class CharacterSchema(O):
	persona     : PersonaSchema
	personality : Personality
	traumas     : list[Trauma]
	dualities   : list[Duality]