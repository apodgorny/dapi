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

	def create_timeline(self, name):
		schema = TimelineSchema(
			title   = name,
			threads = []
		).save(name)
		return schema

	async def invoke(self, name):
		schema = TimelineSchema.load(name)
		if not schema:
			schema = self.create_timeline(name)
		print(schema)
		return 'done'

	async def foobar():
		pass
