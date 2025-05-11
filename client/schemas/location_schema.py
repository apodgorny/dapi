import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib import O


class LocationSchema(O):
	name     : str = O.Field(default='', description='The short name of location')
	location : str = O.Field(default='', description='Where the location is found')
	look     : str = O.Field(default='', description='A visual description of location.')
	feel     : str = O.Field(default='', description='A vibe felt in the location')