from dapi.lib import Datum, OperatorDefinition


################################################################

# Define the square operator class that extends OperatorDefinition
class square(OperatorDefinition):
	class InputType(Datum.Pydantic):
		x: float

	class OutputType(Datum.Pydantic):
		x: float

	def invoke(self, input):
		x = input.x
		return { 'x' : x * x }


################################################################

# Define the double_then_square operator class that extends OperatorDefinition
class double_then_square(OperatorDefinition):
	class InputType(Datum.Pydantic):
		x: float

	class OutputType(Datum.Pydantic):
		x: float

	def invoke(self, input):
		doubled = times_two({'x' : input.x})
		squared = square({'x': doubled['x']})  # Invoke square operator
		return { 'x' : squared.x }


################################################################

# Process class with entry point
class Process:
	entry = double_then_square  # Set the entry point to the double_then_square operator
