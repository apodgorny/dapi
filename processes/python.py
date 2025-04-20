from dapi.lib import Datum, OperatorDefinition


################################################################

# Define input and output types using Pydantic, following naming convention
class square_input(Datum.Pydantic):
    x: float

class square_output(Datum.Pydantic):
    x: float


################################################################

# Define the square operator class that extends OperatorDefinition
class square(OperatorDefinition):
    def invoke(self, input: square_input) -> square_output:
        x = input.x
        return {'x' : x * x}


################################################################

# Process class with entry point
class Process:
    entry = square  # Set the entry point to the square operator
