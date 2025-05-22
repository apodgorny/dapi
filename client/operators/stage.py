import json
from lib import (
	O,
	Operator
)
from client.schemas import (
	BeatSchema
)


class Stage(Operator):
	BEAT_BATCH_SIZE = 5

	class InputType(O):
		story_id      : str
		character_ids : list[str]
		iterations    : int

	class OutputType(O):
		beats : list[BeatSchema]

	async def log(self, beat, clear=False):
		if isinstance(beat, str):
			s = beat
		elif isinstance(beat, dict) or isinstance(beat, list):
			s = json.dumps(beat, indent=4, ensure_ascii=False)
		else:
			s = beat.log()
		await log('beats', s, clear)

	async def add_director_beat(self, story_id, character_ids, beats):
		beat = await director(
			story_id      = story_id,
			character_ids = character_ids,
			beats         = beats[-self.BEAT_BATCH_SIZE:]
		)
		await self.log(beat)
		beats.append(beat)
		return beats

	async def add_character_beat(self, story_id, character_id, beats):
		beat = await character(
			story_id     = story_id,
			character_id = character_id,
			beats        = beats[-self.BEAT_BATCH_SIZE:]
		)
		await self.log(beat)
		beats.append(beat)
		return beats

	async def invoke(self, story_id, character_ids, iterations):
		beats = []

		await self.log(story_id)

		beats = await self.add_director_beat(story_id, character_ids, beats)
		for i in range(iterations):
			for char_id in character_ids:
				beats = await self.add_character_beat(story_id, char_id, beats)

		return beats
