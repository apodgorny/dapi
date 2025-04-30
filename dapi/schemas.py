from pydantic import BaseModel, RootModel, Field, constr
from datetime import datetime
from typing   import Any, Dict, List, Literal
from enum     import Enum


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


class OperatorSchema(BaseModel):
	name        : str             = Field(...,                  description='Operator name')
	class_name  : str             = Field(...,                  description='Class name of operator')
	input_type  : Dict[str, Any]  = Field(...,                  description='Input type name')
	output_type : Dict[str, Any]  = Field(...,                  description='Output type name')
	code        : str | None      = Field(None,                 description='Executable code (ignored for functions)')
	description : str             = Field('',                   description='Human‑readable description')
	scope       : Dict[str, Any]  = Field(default_factory=dict, description='Runtime scope for function operators')
	config      : Dict[str, Any]  = Field(default_factory=dict, description='Configuration passed to interpreter')
	restrict    : bool            = Field(default=True,         description='If True, apply interpreter restrictions')

class OperatorsSchema(BaseModel):
	items: List[OperatorSchema]

class OperatorSetTransactionsSchema(BaseModel):
	name: str
	transaction_ids: List[str]

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

class OperatorScopeSchema(RootModel[Dict[str, Any]]):
	'''Validated dict-like object representing shared scope for a function.'''
	pass

class OperatorInputSchema(BaseModel):
	name  : str
	input : Dict[str, Any]

class OutputSchema(BaseModel):
	output: Dict[str, Any]
