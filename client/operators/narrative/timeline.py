from lib import O, Agent

from client.schemas.narrative_schemas import (
	BeatSchema,
	TimelineSchema,
	ThreadSchema
)

class Timeline(Agent):
	class InputType(O):
		name: str

	class OutputType(O):
		text: str

	async def invoke(self, name):
		schema = TimelineSchema.load(name)
		if not schema:
			schema = TimelineSchema(
				title   = name,
				threads = []
			).save(name)
		print(schema)
		return 'done'
