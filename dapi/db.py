import os
from typing import Any, Dict
from dotenv import load_dotenv

from sqlalchemy     import JSON, String, Text, Integer, create_engine
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, sessionmaker


load_dotenv()

################################################################################
# DB_USER     = os.getenv('DB_USER')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_HOST     = os.getenv('DB_HOST')
# DB_PORT     = os.getenv('DB_PORT')
# DB_NAME     = os.getenv('DB_NAME')

# DB_URL       = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
# engine       = create_engine(DB_URL, echo=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
################################################################################

# SQLite connection URL:
# By default, it uses a local SQLite file named 'sqlite.db'.
# You can override this by setting the DB_URL env variable.
DB_URL = os.getenv('DB_URL', 'sqlite:///./sqlite.db')

# For SQLite, we need to disable the same thread check.
engine = create_engine(DB_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
	'''FastAPI-compatible dependency for DB session.'''
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


Base = declarative_base()


# db model for JSON schema types
class TypeTable(Base):
	__tablename__ = 'types'

	name   : Mapped[str]            = mapped_column(String(255), primary_key=True, comment='Unique type name')
	schema : Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False,      comment='Full JSON Schema')

	def __repr__(self) -> str:
		return f'<TypeTable name={self.name!r}>'

	def to_dict(self) -> Dict[str, Any]:
		return {
			'name'  : self.name,
			'schema': self.schema,
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'TypeTable':
		return cls(name=data['name'], schema=data['schema'])


# db model for operators (atomic static/dynamic/composite)
class OperatorTable(Base):
	__tablename__ = 'operators'

	name         : Mapped[str]  = mapped_column(String(255), primary_key=True, comment='Unique operator name')
	description  : Mapped[str]  = mapped_column(Text, nullable=True,            comment='Optional operator description')
	code         : Mapped[str]  = mapped_column(Text, nullable=False,           comment='Source code or prompt')
	interpreter  : Mapped[str]  = mapped_column(String(50), nullable=False,     comment='Interpreter name (e.g. python, llm)')
	input_type   : Mapped[str]  = mapped_column(String(255), nullable=False,    comment='Input type name (foreign key to TypeTable)')
	output_type  : Mapped[str]  = mapped_column(String(255), nullable=False,    comment='Output type name (foreign key to TypeTable)')

	def __repr__(self) -> str:
		return f'<OperatorTable name={self.name!r}>'

	def to_dict(self) -> Dict[str, Any]:
		return {
			'name'        : self.name,
			'description' : self.description,
			'code'        : self.code,
			'interpreter' : self.interpreter,
			'input_type'  : self.input_type,
			'output_type' : self.output_type,
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'OperatorTable':
		return cls(
			name         = data['name'],
			description  = data.get('description'),
			code         = data['code'],
			interpreter  = data['interpreter'],
			input_type   = data['input_type'],
			output_type  = data['output_type'],
		)


# db model for transactions (ephemeral until invoked)
class TransactionTable(Base):
	__tablename__ = 'transactions'

	id           : Mapped[str]            = mapped_column(String(255), primary_key=True, comment='Unique transaction ID')
	function_id  : Mapped[str]            = mapped_column(String(255), nullable=False,   comment='Owning function ID')
	position     : Mapped[int]            = mapped_column(nullable=False,                comment='Order within function')
	operator     : Mapped[str]            = mapped_column(String(255), nullable=False,   comment='Operator name (foreign key to OperatorTable)')
	input        : Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True,           comment='Current input payload')
	output       : Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True,           comment='Output (set after invoke)')

	def __repr__(self) -> str:
		return f'<TransactionTable id={self.id!r}>'

	def to_dict(self) -> Dict[str, Any]:
		return {
			'id'         : self.id,
			'function_id': self.function_id,
			'position'   : self.position,
			'operator'   : self.operator,
			'input'      : self.input,
			'output'     : self.output,
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'TransactionTable':
		return cls(
			id          = data['id'],
			function_id = data['function_id'],
			position    = data['position'],
			operator    = data['operator'],
			input       = data.get('input'),
			output      = data.get('output'),
		)


# db model for assignments (input wiring into transactions)
class AssignmentTable(Base):
	__tablename__ = 'assignments'

	id             : Mapped[str] = mapped_column(String(255), primary_key=True, comment='Unique assignment ID')
	transaction_id : Mapped[str] = mapped_column(String(255), nullable=False,   comment='Transaction ID (foreign key to TransactionTable)')
	r_accessor     : Mapped[str] = mapped_column(String(255), nullable=False,   comment='Read accessor')
	l_accessor     : Mapped[str] = mapped_column(String(255), nullable=False,   comment='Write accessor')

	def __repr__(self) -> str:
		return f'<AssignmentTable id={self.id!r}>'

	def to_dict(self) -> Dict[str, Any]:
		return {
			'id'             : self.id,
			'transaction_id' : self.transaction_id,
			'r_accessor'     : self.r_accessor,
			'l_accessor'     : self.l_accessor,
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'AssignmentTable':
		return cls(
			id             = data['id'],
			transaction_id = data['transaction_id'],
			r_accessor     = data['r_accessor'],
			l_accessor     = data['l_accessor'],
		)


# db model for functions (named composition of transactions)
class FunctionTable(Base):
	__tablename__ = 'functions'

	id          : Mapped[str]            = mapped_column(String(255), primary_key=True, comment='Unique function ID')
	name        : Mapped[str]            = mapped_column(String(255), nullable=False,   comment='User-facing function name')
	description : Mapped[str]            = mapped_column(Text, nullable=True,           comment='Optional description')
	scope       : Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True,           comment='Initial values injected into runtime scope')

	def __repr__(self) -> str:
		return f'<FunctionTable id={self.id!r}>'

	def to_dict(self) -> Dict[str, Any]:
		return {
			'id'         : self.id,
			'name'       : self.name,
			'description': self.description,
			'scope'      : self.scope,
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'FunctionTable':
		return cls(
			id          = data['id'],
			name        = data['name'],
			description = data.get('description'),
			scope       = data.get('scope'),
		)
