import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

from dapi.lib.module import Module
from dapi.lib.datum  import Datum
from dapi.lib.code   import Code
from dapi.lib.client import Client


def main():
	parser = argparse.ArgumentParser(description='Run a DAPI Process from script.')
	parser.add_argument('path', help='Path to Python process file')
	
	args, unknown_args = parser.parse_known_args()
	file_path          = Path(args.path).resolve()
	module_name        = file_path.stem
	definitions        = Client.compile(file_path)
	entry_name         = definitions['entry_name']
	module             = Module.import_module(module_name, str(file_path))
	entry              = getattr(module, entry_name)
	input_type         = getattr(entry, 'InputType')
	cli_parser         = argparse.ArgumentParser()
	defaults           = {}

	for field, model_field in input_type.model_fields.items():
		field_type = model_field.annotation
		if field_type in [str, int, float] : arg_type = field_type
		else                               : arg_type = str
		print(field, model_field.is_required())
		cli_parser.add_argument(
			f'--{field}',
			required = model_field.is_required(),
			type     = arg_type,
			help     = f'{field} ({arg_type.__name__})'
		)
		if model_field.default is not None and not model_field.default:
			defaults[field] = model_field.default 

	print('defaults', defaults)

	cli_args   = cli_parser.parse_args(unknown_args)
	input_dict = vars(cli_args)
	input_dict = { k : input_dict[k] for k in input_dict if input_dict[k] is not None }
	input_dict.update(defaults)

	print('input_dict', input_dict)

	Datum(input_type).validate(input_dict)
	# Client.reset()
	result = Client.invoke(entry_name, input_dict)
	print(result)


if __name__ == '__main__':
	main()
