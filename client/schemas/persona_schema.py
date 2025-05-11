import os, sys

# Add path to project root to access dapi module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing      import Optional

from lib         import O
from .psychology import Personality


class PersonaSchema(O):
	id          : str = O.Field(default='', description='Persona id. Autofilled')
	name        : str = O.Field(default='', description='The character\'s name')
	sex         : str = O.Field(default='', description='The character\'s biological sex')
	age         : int = O.Field(default=0,  description='The character\'s age in years')
	occupation  : str = O.Field(default='', description='The character\'s type of work or hobby')
	pain        : str = O.Field(default='', description='What causes emotional suffering in this character.')
	desire      : str = O.Field(default='', description='What this character deeply wants or longs for.')
	portrait    : str = O.Field(default='', description='Summary of this character\'s personality, values, and inner world.')
	look        : str = O.Field(default='', description='A visual description of this character\'s appearance.')
	mission     : str = O.Field(default='', description='A long term mission that drives character throughout the story')