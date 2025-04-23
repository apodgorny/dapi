# from dapi.db  import TypeRecord
# from dapi.lib import DatumSchemaError, Datum, DapiException, DapiService


# @DapiService.wrap_exceptions()
# class TypeService(DapiService):
#     '''Service for managing types via FastAPI.'''

#     def validate_name(self, name: str) -> None:
#         # Ensure the type name doesn't already exist
#         if self.dapi.db.get(TypeRecord, name):
#             raise DapiException(status_code=400, detail=f'Type `{name}` already exists', severity=DapiException.BEWARE)

#     def require(self, name: str) -> TypeRecord:
#         # Ensure the type exists
#         record = self.dapi.db.get(TypeRecord, name)
#         if not record:
#             raise DapiException(status_code=404, detail=f'Type `{name}` does not exist', severity=DapiException.HALT)
#         return record
        
#     async def has(self, name: str) -> bool:
#         """Check if a type exists by name."""
#         return self.dapi.db.get(TypeRecord, name) is not None

#     ############################################################################

#     async def create(self, name: str, schema: dict) -> str:
#         self.validate_name(name)

#         # Create TypeRecord in the database
#         record = TypeRecord(name=name, schema=schema)
#         self.dapi.db.add(record)
#         self.dapi.db.commit()

#         return name

#     async def get(self, name: str) -> dict:
#         # Retrieve a type by its name
#         record = self.require(name)
#         return {'name': record.name, 'schema': record.schema}

#     async def get_all(self) -> list[dict]:
#         # Get all types from the database
#         types = self.dapi.db.query(TypeRecord).all()
#         return [{'name': t.name, 'schema': t.schema} for t in types]

#     async def delete(self, name: str) -> None:
#         # Delete a type by its name
#         record = self.require(name)
#         self.dapi.db.delete(record)
#         self.dapi.db.commit()
