from dapi.lib import Datum, Operator


################################################################

# Define the square operator class that extends Operator
class increment(Operator):
	class InputType(Datum.Pydantic):
		x: float

	class OutputType(Datum.Pydantic):
		x: float

	def invoke(self, input):
		x = input.x
		return { 'x' : x + 1 }

################################################################

class main(Operator):
	class InputType(Datum.Pydantic):
		x: float

	class OutputType(Datum.Pydantic):
		x: float

	def invoke(self, input):
		#...

################################################################

# Process class with entry point
class Process:
	entry = main  # Set the entry point to the main operator
