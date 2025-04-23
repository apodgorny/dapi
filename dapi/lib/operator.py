# dapi/lib/operator.py

from dapi.lib import Datum


class Operator:
	'''Base interface for any executable operator: static, dynamic, composite.'''

	def __init__(
		self,
		name   : str,
		input  : Datum,
		output : Datum,
		config : dict = {}
	):
		self.name    = name
		self.input   = input
		self.output  = output
		self.config  = config

		# Inject other operators, so that they could be used in this scope
		globals().update(self.config.dapi.operator_service.plugin_operator_functions)

	async def invoke(self) -> Datum:
		'''Execute operator and return output Datum.'''
		pass

	def __repr__(self) -> str:
		return f'<Operator {self.name}>'
