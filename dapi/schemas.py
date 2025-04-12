from pydantic import BaseModel, Field
from typing   import Any, Dict, List, Literal
from enum     import Enum

# Interpreter Enum (dynamic version, commented until InterpreterRegistry is ready)
# ###########################################################################

# class InterpreterEnum(str, Enum):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate_dynamic
#
#     @classmethod
#     def validate_dynamic(cls, v):
#         from dapi.registry import InterpreterRegistry
#         if v not in InterpreterRegistry.get_names():
#             raise ValueError(f'Interpreter "{v}" is not available')
#         return v


# Interpreter Enum (static for now)
###########################################################################

class InterpreterEnum(str, Enum):
	python = 'python'
	llm    = 'llm'


# Generic schemas
###########################################################################

class StatusSchema(BaseModel):
	status: str = Field(..., description='Operation status message')

class NameSchema(BaseModel):
	name: str = Field(..., description='Entity name')

class IdSchema(BaseModel):
	id: str = Field(..., description='Entity id')

class EmptySchema(BaseModel):
	pass 


# TYPE schemas
###########################################################################

class TypeSchema(BaseModel):
	name   : str
	schema : dict

class TypesSchema(BaseModel):
	items: List[TypeSchema]


# OPERATOR schemas
###########################################################################

class OperatorSchema(BaseModel):
	name        : str             = Field(..., description='Operator name')
	input_type  : str             = Field(..., description='Input type name')
	output_type : str             = Field(..., description='Output type name')
	code        : str             = Field(..., description='Executable code')
	description : str             = Field('',  description='Human‑readable description')
	interpreter : InterpreterEnum = Field(..., description='Execution backend')

class OperatorsSchema(BaseModel):
	items: List[OperatorSchema]


# TRANSACTION schemas
###########################################################################

class TransactionCreateSchema(BaseModel):
	operator: str = Field(..., description='Operator to invoke')

class TransactionSchema(BaseModel):
	id      : str = None
	operator: str

class TransactionsSchema(BaseModel):
	items: List[TransactionSchema]


# ASSIGNMENT schemas
###########################################################################

class AssignmentSchema(BaseModel):
	id             : str = None
	transaction_id : str = Field(..., description='Target transaction')
	l_accessor     : str = Field(..., description='Accessor to assign to (target)')
	r_accessor     : str = Field(..., description='Accessor to assign from (source)')

class AssignmentsSchema(BaseModel):
	items: List[AssignmentSchema]


# INVOCATION schemas
###########################################################################

class OperatorInputSchema(BaseModel):
	name  : str
	input : Dict[str, Any]

class TransactionInputSchema(BaseModel):
	name  : str
	input : Dict[str, Any]

class OutputSchema(BaseModel):
	output: Dict[str, Any]


# FUNCTION / COMPOSITE schemas
###########################################################################

class FunctionSchema(BaseModel):
	name       		: str
	interpreter     : InterpreterEnum
	transaction_ids : List[str]
	scope           : Dict[str, Any]
