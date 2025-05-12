import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib import O

class RelationSchema(O):
	relator_id : str = O.Field('', description='ID of the character whose disposition is being described')
	relatee_id : str = O.Field('', description='ID of the character toward whom the disposition is directed')
	expression : str = O.Field('', description='A short first-person phrase describing the relator’s feelings or attitude, e.g., "I trust him/her, but I fear his/her silence."')

class RelationsSchema(O):
	relations : list[RelationSchema] = O.Field('', description='List of all interpersonal relations between characters')
