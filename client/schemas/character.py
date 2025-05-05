import os, sys

# Add path to project root to access dapi module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing      import Optional

from dapi.lib    import O
from .psychology import Personality, Trauma, Duality
from .persona    import Persona


class Character(O):
	persona     : Persona
	personality : Personality
	traumas     : list[Trauma]
	dualities   : list[Duality]