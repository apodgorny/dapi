from lib.client import Client

# Create number type schema
number_type = {
	'title'     : 'number_type',
	'type'      : 'object',
	'properties': {
		'x': { 'type': 'number' }
	},
	'required': ['x']
}

# Create the type if it doesn't exist already
Client.create_type('number_type', number_type)

# Create the plugin operator
Client.create_operator(
	name        = 'times_two',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = '',  # Not used for plugin operators
	interpreter = 'plugin',
	config      = {}  # Optional configuration if needed
)

# Test the plugin operator
input_data = {'x': 21}
print('Input:', input_data)
result = Client.invoke('times_two', input_data)
print('Result:', result)
