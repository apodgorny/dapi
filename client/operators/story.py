from typing import List, Dict, Any

from lib import (
	O,
	Operator,
	String
)
from client.schemas import (
	LocationSchema,
	StorySchema
)


class Story(Operator):

	class InputType(O):
		title      : str
		genre      : str
		variations : int
		locations  : int

	class OutputType(O):
		story : StorySchema

	async def invoke(self, title, genre, variations, locations):
		variation = await variations(
			title  = title,
			genre  = genre,
			spread = variations
		)
		story_idea = await idea(
			title     = title,
			variation = variation,
			genre     = genre
		)
		story_locations = await locations(
			title  = variation,
			genre  = genre,
			idea   = story_idea,
			spread = locations
		)
		id   = String.slugify(title)
		data = StorySchema(
			id        = id,
			title     = title,
			variation = variation,
			genre     = genre,
			idea      = story_idea,
			locations = story_locations
		)
		foo = await write_json(f'story.{id}.json', data.to_dict())
		return data

