from typing   import Any, Callable, Type, List, Dict

from fastapi           import FastAPI, APIRouter, Depends
from pydantic          import BaseModel, create_model, Field
from fastapi.responses import JSONResponse
from sqlalchemy.orm    import Session

from dapi.db import get_db
from dapi.schemas import (
    # inputs
    CreateTypeInputSchema,
    GetTypeInputSchema,
    ListTypesInputSchema,
    DeleteTypeInputSchema,
    CreateOperatorInputSchema,
    ListOperatorsInputSchema,
    DeleteOperatorInputSchema,
    CreateTransactionInputSchema,
    CreateTransactionAssignmentInputSchema,
    InvokeTransactionInputSchema,
    ListTransactionsInputSchema,
    DeleteTransactionInputSchema,
    CreateScopeInputSchema,
    # outputs
    TypeInfoSchema,
    ListTypesOutputSchema,
    OperatorInfoSchema,
    ListOperatorsOutputSchema,
    TransactionInfoSchema,
    ListTransactionsOutputSchema,
    AssignmentInfoSchema,
    InvokeTransactionOutputSchema,
    ScopeInfoSchema
)
from dapi.services import TypeService

# ---------------------------------------------------------------------------
# Local helper schemas
# ---------------------------------------------------------------------------

class StatusOutputSchema(BaseModel):
    status: str

# ---------------------------------------------------------------------------
# Router & dynamic registration helper
# ---------------------------------------------------------------------------

router = APIRouter(prefix='/dapi')

def start_dapi(dapi: FastAPI):
    dapi.include_router(router)
    print('Hello, DAPI!')


def define(
    path          : str,
    input_model   : Type[Any],
    output_model  : Type[Any],
    invoke_handler: Callable[[Any], Any],
    description   : str = ''
):
    '''Registers a DAPI operator route dynamically.'''

    async def endpoint(input: input_model):  # type: ignore[name-defined]
        return await invoke_handler(input)  # type: ignore[name-defined]

    endpoint.__name__ = f'dapi_{path.strip("/").replace("/", "_")}_handler'
    endpoint.__doc__  = description

    router.add_api_route(
        path           = f'/{path.strip("/")}',
        endpoint       = endpoint,
        methods        = ['POST'],
        response_model = output_model,
        name           = f'dapi:{path}',
        response_class = JSONResponse,
        description    = description
    )

# ---------------------------------------------------------------------------
# Example dynamic operator
# ---------------------------------------------------------------------------

ExampleInput  = create_model('ExampleInput',  value=(int, Field(...)))
ExampleOutput = create_model('ExampleOutput', value=(int, Field(...)))

async def double_handler(input: ExampleInput) -> ExampleOutput:  # type: ignore[arg-type]
    return ExampleOutput(value=input.value * 2)

define('double', ExampleInput, ExampleOutput, double_handler, description='Doubles the input value')

# ---------------------------------------------------------------------------
# TYPE endpoints
# ---------------------------------------------------------------------------

@router.post('/create_type', response_model=TypeInfoSchema)
async def create_type(input: CreateTypeInputSchema, db: Session = Depends(get_db)):
	'''Creates a new type in the DAPI system using a name and JSON schema.'''
	service = TypeService(db)
	service.create(name=input.name, schema=input.schema)
	return TypeInfoSchema(name=input.name, schema=input.schema)


@router.post('/get_type', response_model=TypeInfoSchema)
async def get_type(input: GetTypeInputSchema, db: Session = Depends(get_db)):
	'''Returns a single type definition by name.'''
	service = TypeService(db)
	record = service.get(input.name)
	return TypeInfoSchema(**record)


@router.post('/get_all_types', response_model=ListTypesOutputSchema)
async def get_all_types(input: ListTypesInputSchema, db: Session = Depends(get_db)):
	'''Returns a list of all registered types with full definitions.'''
	service = TypeService(db)
	records = service.get_all()
	return ListTypesOutputSchema(data=[TypeInfoSchema(**r) for r in records])


@router.post('/delete_type', response_model=StatusOutputSchema)
async def delete_type(input: DeleteTypeInputSchema, db: Session = Depends(get_db)):
	'''Removes a type from the system by name.'''
	service = TypeService(db)
	service.delete(input.name)
	return {'status': 'deleted'}
	
# ---------------------------------------------------------------------------
# OPERATOR endpoints
# ---------------------------------------------------------------------------

@router.post('/create_operator', response_model=OperatorInfoSchema)
async def create_operator(input: CreateOperatorInputSchema):
    '''Defines a new operator by name, input/output types, and executable code.'''
    # TODO: OperatorService.save_operator
    return OperatorInfoSchema(**input.model_dump())


@router.post('/list_operators', response_model=ListOperatorsOutputSchema)
async def list_operators(input: ListOperatorsInputSchema):
    '''Returns a list of all registered operators.'''
    # TODO: OperatorService.list_operators
    return ListOperatorsOutputSchema(data=[])


@router.post('/delete_operator', response_model=StatusOutputSchema)
async def delete_operator(input: DeleteOperatorInputSchema):
    '''Removes an operator from the system by name.'''
    # TODO: OperatorService.delete_operator
    return {'status': 'deleted'}

# ---------------------------------------------------------------------------
# TRANSACTION endpoints
# ---------------------------------------------------------------------------

@router.post('/create_transaction', response_model=TransactionInfoSchema)
async def create_transaction(input: CreateTransactionInputSchema):
    '''Creates a transaction that wraps the invocation of a given operator.'''
    # TODO: TransactionService.create_transaction
    return TransactionInfoSchema(id='tx_1', operator=input.operator)


@router.post('/create_transaction_assignment', response_model=AssignmentInfoSchema)
async def create_transaction_assignment(input: CreateTransactionAssignmentInputSchema):
    '''Creates an assignment that transfers values into the transaction input.'''
    # TODO: AssignmentService.create
    return AssignmentInfoSchema(id='as_1', **input.model_dump())


@router.post('/invoke_transaction', response_model=InvokeTransactionOutputSchema)
async def invoke_transaction(input: InvokeTransactionInputSchema):
    '''Runs a transaction and returns its output; then deletes the transaction.'''
    # TODO: TransactionService.invoke
    return InvokeTransactionOutputSchema(output={'value': 42})


@router.post('/list_transactions', response_model=ListTransactionsOutputSchema)
async def list_transactions(input: ListTransactionsInputSchema):
    '''Returns a list of existing transactions (if not yet invoked).'''
    return ListTransactionsOutputSchema(data=[])


@router.post('/delete_transaction', response_model=StatusOutputSchema)
async def delete_transaction(input: DeleteTransactionInputSchema):
    '''Removes a transaction from the system before it is invoked.'''
    # TODO: TransactionService.delete
    return {'status': 'deleted'}

# ---------------------------------------------------------------------------
# SCOPE endpoint
# ---------------------------------------------------------------------------

@router.post('/create_scope', response_model=ScopeInfoSchema)
async def create_scope(input: CreateScopeInputSchema):
    '''Creates a composite operator from transaction chain and shared scope.'''
    # TODO: ScopeService.create
    return ScopeInfoSchema(**input.model_dump())
