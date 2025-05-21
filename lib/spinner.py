from .operator import Operator
from .o        import O
from .string   import String
from .agent    import Agent

from dapi.schemas import (
	SpinnerCriteriaSchema,
	SpinnerStructureSchema
)


class Spinner(Agent):
	class OutputType(O):
		text : str

	class InputType(O):
		prompt : str = None
		spin   : str = None

	class PromptType(O):
		prompt : str

	class CriteriaType(O):
		criteria : SpinnerCriteriaSchema

	class StructureType(O):
		spins : SpinnerStructureSchema

	class Templates:
		spin_in           = ''
		spins             = {}
		spin_out          = ''
		generate_criteria = ''

	async def spin(self, verbose=False, ** template_vars):
		if hasattr(self.Templates, 'spins'):
			spins = self.Templates.spins
		else:
			spins = (await self.generate_spin_structure(** template_vars))['spins']

		hr      = '-'*20
		spin_in = self.fill(self.Templates.spin_in, ** template_vars)
		prompts = [ spin_in ]

		for title in spins:
			self.log('TITLE', title)
			spin_query  = self.fill(spins[title], ** template_vars)
			spin_prompt = '\n'.join(prompts + [hr, 'YOUR TASK:', spin_query, hr])
			spin_value  = await self.ask(spin_prompt, self.PromptType)

			prompts.append(f'BEGIN "{title}":\n{spin_value}\nEND "{title}"')

		spin_out = self.fill(self.Templates.spin_out, ** template_vars)
		prompt   = '\n'.join(prompts + [hr, 'YOUR TASK:', spin_out, hr])

		return await self.ask(prompt, self.OutputType)

	async def generate_spin_criteria(self, ** template_vars):
		prompt = self.fill(self.Templates.generate_spin_criteria, ** template_vars)
		return await self.ask(prompt, self.CriteriaType)

	async def generate_spin_structure(self, ** template_vars):
		criteria = await self.generate_spin_criteria(** template_vars)
		template_vars['spin_criteria'] = criteria
		prompt = self.fill(self.Templates.generate_spin_structure, ** template_vars)
		return await self.ask(prompt, self.StructureType)

