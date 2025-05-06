import os, sys

# Add path to project root to access dapi module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing      import Optional

from lib         import O
from .psychology import Personality


class Persona(O):
	name        : str = O.Field(default='', description='The person\'s name')
	sex         : str = O.Field(default='', description='The person\'s biological sex')
	age         : int = O.Field(default=0,  description='The person\'s age in years')
	occupation  : str = O.Field(default='', description='The person\'s type of work or hobby')
	pain        : str = O.Field(default='', description='What causes emotional suffering in this person.')
	desire      : str = O.Field(default='', description='What this person deeply wants or longs for.')
	portrait    : str = O.Field(default='', description='Summary of this person\'s personality, values, and inner world.')
	look        : str = O.Field(default='', description='A visual description of this person\'s appearance.')
