from pydantic import BaseModel, Field
from typing   import Any, Dict, List, Literal
from enum     import Enum

# ---------------------------------------------------------------------------
# Interpreter Enum (dynamic version, commented until InterpreterRegistry is ready)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Interpreter Enum (static for now)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

class InterpreterEnum(str, Enum):
    python = 'python'
    llm    = 'llm'

# ---------------------------------------------------------------------------
# Generic status output
# ---------------------------------------------------------------------------

class StatusOutputSchema(BaseModel):
    status: str = Field(..., description='Operation status message')

# ---------------------------------------------------------------------------
# TYPE schemas
# ---------------------------------------------------------------------------

class CreateTypeInputSchema(BaseModel):
	name   : str
	schema : dict

class TypeInfoSchema(CreateTypeInputSchema):
    """Echoes the stored type definition."""
    pass

class ListTypesInputSchema(BaseModel):
    pass  # empty body for symmetry

class GetTypeInputSchema(BaseModel):
    name: str  # retrieve single type by name

class ListTypesOutputSchema(BaseModel):
    data: List[TypeInfoSchema]

class DeleteTypeInputSchema(BaseModel):
    name: str

class DeleteTypeOutputSchema(StatusOutputSchema):
    pass

# ---------------------------------------------------------------------------
# OPERATOR schemas
# ---------------------------------------------------------------------------

class CreateOperatorInputSchema(BaseModel):
    name        : str            = Field(..., description='Operator name')
    input_type  : str            = Field(..., description='Input type name')
    output_type : str            = Field(..., description='Output type name')
    code        : str            = Field(..., description='Executable code')
    description : str            = Field('',  description='Human‑readable description')
    interpreter : InterpreterEnum = Field(..., description='Execution backend')

class OperatorInfoSchema(CreateOperatorInputSchema):
    pass

class ListOperatorsInputSchema(BaseModel):
    pass

class ListOperatorsOutputSchema(BaseModel):
    data: List[OperatorInfoSchema]

class DeleteOperatorInputSchema(BaseModel):
    name: str

class DeleteOperatorOutputSchema(StatusOutputSchema):
    pass

# ---------------------------------------------------------------------------
# TRANSACTION schemas
# ---------------------------------------------------------------------------

class CreateTransactionInputSchema(BaseModel):
    operator: str = Field(..., description='Operator to invoke')

class TransactionInfoSchema(BaseModel):
    id      : str
    operator: str

class ListTransactionsInputSchema(BaseModel):
    pass

class ListTransactionsOutputSchema(BaseModel):
    data: List[TransactionInfoSchema]

class DeleteTransactionInputSchema(BaseModel):
    id: str

class DeleteTransactionOutputSchema(StatusOutputSchema):
    pass

# ---------------------------------------------------------------------------
# ASSIGNMENT schemas
# ---------------------------------------------------------------------------

class CreateTransactionAssignmentInputSchema(BaseModel):
    transaction_id : str            = Field(..., description='Target transaction')
    from_          : Dict[str, Any] = Field(..., alias='from', description='Source value or accessor')
    to             : str            = Field(..., description='Destination accessor')

class AssignmentInfoSchema(CreateTransactionAssignmentInputSchema):
    id: str

# ---------------------------------------------------------------------------
# INVOCATION schemas
# ---------------------------------------------------------------------------

class InvokeTransactionInputSchema(BaseModel):
    transaction_id: str

class InvokeTransactionOutputSchema(BaseModel):
    output: Dict[str, Any]

# ---------------------------------------------------------------------------
# SCOPE / COMPOSITE schemas
# ---------------------------------------------------------------------------

class CreateScopeInputSchema(BaseModel):
    name       : str
    tx_ids     : List[str]
    interpreter: InterpreterEnum
    scope      : Dict[str, Any]

class ScopeInfoSchema(CreateScopeInputSchema):
    pass
