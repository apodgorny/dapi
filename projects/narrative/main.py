import sys, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
	sys.path.insert(0, ROOT)

from wordwield import ww

print('here')

from schemas.schemas import (
	BeatSchema,
	TimelineSchema,
	ThreadSchema,
	VoiceSchema
)
from operators import (
	Pipeline,
	# Test
)
print('and here')
################################################################

ww.verbose = True
result = ww.invoke(Pipeline, name='pipeline')