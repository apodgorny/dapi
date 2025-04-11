from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi import HTTPException

from dapi.db import TypeTable
from dapi.lib.datum import DatumSchemaError, Datum


class TypeService:
	'''Service for managing JSON Schema types via SQLAlchemy.'''

	def __init__(self, session: Session) -> None:
		self.session = session

	def _assert_does_not_exist(self, name: str) -> None:
		if self.session.get(TypeTable, name):
			raise HTTPException(status_code=400, detail=f'Type `{name}` already exists')

	def _get_assert_exists(self, name: str) -> None:
		record = self.session.get(TypeTable, name)
		if not record:
			raise HTTPException(status_code=404, detail=f'Type `{name}` does not exist')
		return record

	def create(self, name: str, schema: dict) -> str:
		self._assert_does_not_exist(name)
		try:
			Datum.assert_valid_jsonschema(schema)
		except DatumSchemaError as exc:
			raise HTTPException(status_code=422, detail=str(exc))

		record = TypeTable(name=name, schema=schema)
		self.session.add(record)
		self.session.commit()
		return name

	def get(self, name: str) -> dict:
		record = self._get_assert_exists(name)
		return record.to_dict()

	def get_all(self) -> list[dict]:
		return [type_.to_dict() for type_ in self.session.query(TypeTable).all()]

	def delete(self, name: str) -> None:
		record = self._get_assert_exists(name)
		self.session.delete(record)
		self.session.commit()
