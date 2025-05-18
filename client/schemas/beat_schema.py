import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib import O


class DirectorBeatSchema(O):
	character_id : str = '-- setting --'
	line         : str = O.Field(default='', description='Declaration that appears as narrators voice' )

class BeatSchema(O):
	character_id : str = O.Field(description='Id of character acting. Autofilled' )
	speech       : str = O.Field(description='Direct speech of character' )
	action       : str = O.Field(description='Direct action of character. One sentence' )

	def prompt(self):
		name = ' '.join([w.capitalize() for w in self.character_id.split('-')])
		return f'{name}: "{self.speech}"' + (f'[{self.action}]' if self.action else '')

	# feeling         : str       = O.Field(default='', description='What does character feel if any. Inner expression of mood' )
	# thought         : str       = O.Field(default='', description='What does character think if any' )
	# desire          : str       = O.Field(default='', description='What does character REALLY want right now, but would not admit' )

	# action          : str       = O.Field(default='', description='What is character doing right now: going, touching, building, playing' )
	# expression      : str       = O.Field(default='', description='Jesture of facial expression that character does. Visible expression of mood' )
	# line            : str       = O.Field(default='', description='Speech. Vocalization. The actual line the character sais aloud, if any' )

	# target_ids      : list[str] = O.Field(default=[], description='If something is said, or expressed – to whom? List character ids' )