from dapi.lib import Datum, OperatorDefinition


################################################################

# Define input and output types using Pydantic, following naming convention
class square_input(Datum.Pydantic):
    x: float

class square_output(Datum.Pydantic):
    x: float


class double_then_square_input(Datum.Pydantic):
    x: float

class double_then_square_output(Datum.Pydantic):
    x: float


################################################################

# Define the square operator class that extends OperatorDefinition
class square(OperatorDefinition):
    def invoke(self, input: square_input) -> square_output:
        x = input.x
        return { 'x' : x * x }


################################################################

# Define the double_then_square operator class that extends OperatorDefinition
class double_then_square(OperatorDefinition):
    def invoke(self, input: double_then_square_input) -> double_then_square_output:
        doubled = input.x * 2
        squared = square({'x': doubled})  # Invoke square operator
        return { 'x' : squared.x }


################################################################

# Process class with entry point
class Process:
    entry = double_then_square  # Set the entry point to the double_then_square operator
