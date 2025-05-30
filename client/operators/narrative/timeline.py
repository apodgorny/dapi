from lib import O, Agent

from client.schemas.narrative_schemas import (
	BeatSchema,
	TimelineSchema,
	ThreadSchema
)

class Timeline(Agent):
	class InputType(O):
		text: str

	class OutputType(O):
		text: str

	async def invoke(self, text):
		# beat = BeatSchema(
		# 	timestamp = 123,
		# 	text      = 'foobar'
		# )
		# voice = VoiceSchema(
		# 	name   = 'test',
		# 	tone   = 'neutral',
		# 	style  = 'flat',
		# 	intent = 'say something'
		# )

		voice = VoiceSchema.load('v1')
		print(voice)

		return 'done'
