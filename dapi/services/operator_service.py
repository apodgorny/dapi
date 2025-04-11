from __future__ import annotations

from fastapi import HTTPException

from dapi.db import OperatorTable
# from dapi.services.interpreter_service import InterpreterService


class OperatorService:
	'''Service for managing operators: atomic_static, atomic_dynamic, composite.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	def validate_name(self, name: str) -> None:
		if self.dapi.db.get(OperatorTable, name):
			raise HTTPException(status_code=400, detail=f'Operator `{name}` already exists')

	def require(self, name: str) -> OperatorTable:
		record = self.dapi.db.get(OperatorTable, name)
		if not record:
			raise HTTPException(status_code=404, detail=f'Operator `{name}` does not exist')
		return record

	def validate_io(self, schema):
		if not self.dapi.type_service.has(schema.input_type):
			raise HTTPException(status_code=404, detail=f'Type `{schema.input_type}` specified in `{schema.name}.input_type` does not exist')
		if not self.dapi.type_service.has(schema.output_type):
			raise HTTPException(status_code=404, detail=f'Type `{schema.output_type}` specified in `{schema.name}.output_type` does not exist')

	# def validate_interpreter(self, interpreter):
	# 	if not self.dapi.interpreter_service.has(schema.interpreter):
	# 		raise HTTPException(status_code=404, detail=f'Interpreter `{schema.interpreter}` specified in `{schema.name}.interpreter` does not exist')

	############################################################################

	def create(self, schema: OperatorSchema) -> str:
		self.validate_name(schema.name)
		self.validate_io(schema)
		# self.validate_interpreter(schema.interpreter)

		record = OperatorTable(**schema.model_dump())

		self.dapi.db.add(record)
		self.dapi.db.commit()

		# Register with define()
		self.define(
			name        = schema.name,
			input_type  = schema.input_type,
			output_type = schema.output_type,
			interpreter = schema.interpreter,
			code        = schema.code,
			description = schema.description,
		)

		return schema.name

	def get(self, name: str) -> dict:
		record = self.require(name)
		return record.to_dict()

	def get_all(self) -> list[dict]:
		return [op.to_dict() for op in self.dapi.db.query(OperatorTable).all()]

	def delete(self, name: str) -> None:
		record = self.require(name)
		self.dapi.db.delete(record)
		self.dapi.db.commit()

