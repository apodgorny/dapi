# Add Python's sys.path manipulation to ensure imports work correctly
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['CLIENT'] = __file__
DATA_DIR = os.environ.get('DATA_DIR')

# from lib.debug import debugpy

# Use absolute imports to avoid issues when running script directly
from client.schemas.narrative_schemas import (
	BeatSchema,
	TimelineSchema,
	ThreadSchema,
	VoiceSchema
)
from client.operators.narrative import (
	Timeline
)

from lib import WordWield as ww


################################################################

ww.invoke(Timeline, text = 'foobar')