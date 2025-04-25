import os
import uuid
import enum

from typing                         import Any, Dict
from datetime                       import datetime

from dotenv                         import load_dotenv
from sqlalchemy                     import Column, Enum, String, Text, DateTime, create_engine, JSON
from sqlalchemy.orm                 import Mapped, mapped_column, declarative_base, sessionmaker
from sqlalchemy.ext.declarative     import DeclarativeMeta
from sqlalchemy.ext.mutable         import MutableDict
from sqlalchemy.dialects.postgresql import UUID


load_dotenv()

DB_URL                = os.getenv('DB_URL')
engine                = create_engine(DB_URL, connect_args={'check_same_thread': False}, echo=False)
SessionLocal          = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base: DeclarativeMeta = declarative_base()


# Base model class
#####################################################################

class Record(Base):
	__abstract__ = True
	def to_dict(self) -> Dict[str, Any]:
		result = {}
		for c in self.__table__.columns:
			value = getattr(self, c.name)
			if isinstance(value, enum.Enum):
				value = value.value
			result[c.name] = value
		return result

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'TableBase':
		return cls(**data)


# JSON schema types
#####################################################################

# class TypeRecord(Record):
# 	__tablename__ = 'types'

# 	name   : Mapped[str]            = mapped_column(String(255), primary_key=True, comment='Unique type name')
# 	schema : Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False,          comment='Full JSON Schema')


# # Operators (atomic static/dynamic/composite)
# #####################################################################

# class OperatorRecord(Record):
# 	__tablename__ = 'operators'

# 	name         : Mapped[str]             = mapped_column(String(255),                  primary_key=True, comment='Unique operator name')
# 	description  : Mapped[str]             = mapped_column(Text,                         nullable=True,    comment='Optional operator description')
# 	code         : Mapped[str]             = mapped_column(Text,                         nullable=True,    comment='Source code or prompt (or empty for composite)')
# 	interpreter  : Mapped[str]             = mapped_column(String(50),                   nullable=False,   comment='Interpreter name (e.g. python, llm, composite)')
# 	input_type   : Mapped[str]             = mapped_column(String(255),                  nullable=False,   comment='Input type name (foreign key to TypeTable)')
# 	output_type  : Mapped[str]             = mapped_column(String(255),                  nullable=False,   comment='Output type name (foreign key to TypeTable)')
# 	# transactions : Mapped[list[str]]       = mapped_column(JSON,                         default=list,     comment='List of transaction IDs for function operators')
# 	scope        : Mapped[Dict[str, Any]]  = mapped_column(MutableDict.as_mutable(JSON), default=dict,     comment='Runtime scope for function operators')
# 	config       : Mapped[Dict[str, Any]]  = mapped_column(MutableDict.as_mutable(JSON), default=dict,     comment='Configuration passed to interpreter')

# class TypeRecord(Record):
# 	__tablename__ = 'types'

# 	name   : Mapped[str]            = mapped_column(String(255), primary_key=True, comment='Unique type name')
# 	schema : Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False,          comment='Full JSON Schema')


# Operators (atomic static/dynamic/composite)
#####################################################################

class OperatorRecord(Record):
	__tablename__ = 'operators'

	name         : Mapped[str]             = mapped_column(String(255),                  primary_key=True, comment='Unique operator name')
	class_name   : Mapped[str]             = mapped_column(String(255),                  nullable=False,   comment='Unique operator class name')
	description  : Mapped[str]             = mapped_column(Text,                         nullable=True,    comment='Optional operator description')
	code         : Mapped[str]             = mapped_column(Text,                         nullable=True,    comment='Source code or prompt (or empty for composite)')
	interpreter  : Mapped[str]             = mapped_column(String(50),                   nullable=False,   comment='Interpreter name (e.g. python, llm, composite)')
	
	input_type   : Mapped[Dict[str, Any]]  = mapped_column(JSON,                         nullable=False,   comment='Full JSON Schema')
	output_type  : Mapped[Dict[str, Any]]  = mapped_column(JSON,                         nullable=False,   comment='Full JSON Schema')

	scope        : Mapped[Dict[str, Any]]  = mapped_column(MutableDict.as_mutable(JSON), default=dict,     comment='Runtime scope for function operators')
	config       : Mapped[Dict[str, Any]]  = mapped_column(MutableDict.as_mutable(JSON), default=dict,     comment='Configuration passed to interpreter')

class OperatorInstanceStatus(enum.Enum):
	created = 'created'
	running = 'running'
	invoked = 'invoked'
	error   = 'error'

# class OperatorInstanceRecord(Record):
# 	__tablename__ = 'runtime'

# 	id          = Column(String(36),                  primary_key=True, default=lambda: str(uuid.uuid4()),     comment='Instance ID')
# 	name        = Column(String,                       nullable=True,                                          comment='Optional instance name (used in composite scope)')
# 	operator    = Column(String,                       nullable=False,                                         comment='Operator name this instance runs')

# 	input       = Column(JSON,                         nullable=False,                                         comment='Input data for operator')
# 	output      = Column(JSON,                         default=dict,                                           comment='Result of execution')

# 	status      = Column(Enum(OperatorInstanceStatus), nullable=False, default=OperatorInstanceStatus.created, comment='Execution status')
# 	error       = Column(Text,                         nullable=True,                                          comment='Error message if any')

# 	children    = Column(JSON,                         default=list,                                           comment='IDs of child operator instances')

# 	created_at  = Column(DateTime,                     default=datetime.utcnow,                                comment='Creation timestamp')
# 	invoked_at  = Column(DateTime,                     nullable=True,                                          comment='Time of successful invocation')


# # Transactions (ephemeral until invoked)
# #####################################################################

# class TransactionRecord(Record):
# 	__tablename__ = 'transactions'

# 	id          : Mapped[str]            = mapped_column(String(255), primary_key=True, comment='Unique transaction ID')
# 	name        : Mapped[str]            = mapped_column(String(255), nullable=False,   comment='Step name used in scope')
# 	operator    : Mapped[str]            = mapped_column(String(255), nullable=False,   comment='Operator to invoke')
# 	input       : Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True,           comment='Runtime input payload')
# 	output      : Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True,           comment='Runtime output after invoke')


# # Assignments (input wiring into transactions)
# #####################################################################

# class AssignmentRecord(Record):
# 	__tablename__ = 'assignments'

# 	id             : Mapped[str] = mapped_column(String(255), primary_key=True, comment='Unique assignment ID')
# 	transaction_id : Mapped[str] = mapped_column(String(255), nullable=False,   comment='Transaction ID (foreign key to TransactionTable)')
# 	r_accessor     : Mapped[str] = mapped_column(String(255), nullable=False,   comment='Read accessor')
# 	l_accessor     : Mapped[str] = mapped_column(String(255), nullable=False,   comment='Write accessor')
