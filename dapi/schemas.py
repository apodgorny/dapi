from pydantic import BaseModel, Field, constr
from datetime import datetime
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


# Interpreter Enum (extended static version)
###########################################################################

class InterpreterEnum(str, Enum):
	python   = 'python'
	llm      = 'llm'
	function = 'function'  # Executes a list of transactions defined in meta.definition


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

class FunctionDefinitionSchema(BaseModel):  # Matches structure of meta.definition for interpreter='function'
	transactions : List[str]      = Field(..., description='Transaction chain for function operator')
	scope        : Dict[str, Any] = Field(default_factory=dict, description='Initial runtime scope')

class OperatorSchema(BaseModel):
	name        : str             = Field(...,  description='Operator name')
	input_type  : str             = Field(...,  description='Input type name')
	output_type : str             = Field(...,  description='Output type name')
	code        : str | None      = Field(None, description='Executable code (ignored for functions)')
	description : str             = Field('',   description='Human‑readable description')
	interpreter : InterpreterEnum = Field(...,  description='Execution backend')
	meta        : dict | None     = Field(None, description='Interpreter-specific metadata')

class OperatorsSchema(BaseModel):
	items: List[OperatorSchema]

class OperatorInstanceSchema(BaseModel):
	id         : str
	operator   : str
	input      : dict
	output     : dict = Field(default_factory=dict)
	status     : Literal['created', 'running', 'invoked', 'error'] = 'created'
	error      : str | None = None
	children   : list[str] = Field(default_factory=list)
	created_at : datetime = Field(default_factory=datetime.utcnow)
	invoked_at : datetime | None = None


# TRANSACTION schemas
###########################################################################

class TransactionCreateSchema(BaseModel):
	operator: str = Field(..., description='Operator to invoke')

class TransactionSchema(BaseModel):
	id          : str | None = None
	name        : str        = Field(..., description='Unique name under which this step is stored in scope')
	operator    : str        = Field(..., description='Operator to invoke')
	function_id : str | None = None  # ID of owning composite operator

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
	name  : constr(min_length=1)
	input : Dict[str, Any]

class OutputSchema(BaseModel):
	output: Dict[str, Any]
