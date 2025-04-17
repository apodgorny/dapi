from dapi.lib.operator import Operator


class TimesTwo(Operator):
	'''Plugin operator that multiplies input by two.'''
	
	input_type  = 'number_type'
	output_type = 'number_type'
	
	@classmethod
	def invoke(cls, input_data, config=None):
		'''Multiply input.x by 2 and return as output.x.'''
		return {'x': input_data['x'] * 2}
