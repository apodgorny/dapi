from .operator import Operator
from .o        import O
from .string   import String
from .agent    import Agent


class Respin(Agent):
	class OutputType(O):
		text : str

	class InputType(O):
		prompt : str = None
		spin   : str = None

	class PromptType(O):
		prompt : str

	class Templates:
		identity : str
		spins    : list[str]

	async def spin(self, verbose=False, ** template_vars):
		spin_in = self.fill(self.Templates.spin_in, ** template_vars)
		if verbose:
			print('-'*30)
			print('SPIN IN')
			print(spin_in)
			print('-'*30)
		prompts     = [ spin_in ]
		n_templates = len(self.Templates.spins)

		for n in range(n_templates):
			spin_template = self.Templates.spins[n]
			spin_prompt   = self.fill(spin_template, ** template_vars)
			hr            = '*'*20
			prompt        = '\n'.join(prompts + [hr, 'YOUR TASK:', spin_prompt, hr])
			addendum      = await self.ask(prompt, self.PromptType)

			if verbose:
				print('-'*30)
				print('PROMPT')
				print('-'*30)
				print(prompt)
				print('-'*30)
				print('ADDENDUM')
				print('-'*30)
				print(addendum)
				print('-'*30)

			prompts.append(addendum)

		spin_out_prompt = self.fill(self.Templates.spin_out, ** template_vars)
		hr              = '*'*20
		prompt          = '\n'.join(prompts + [hr, 'YOUR TASK:', spin_out_prompt, hr])

		return await self.ask(prompt, self.OutputType)
