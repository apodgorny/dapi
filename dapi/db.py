import os
import uuid
import enum

from typing                         import Any, Dict
from datetime                       import datetime

from dotenv                         import load_dotenv
from sqlalchemy                     import Column, Enum, String, Text, DateTime, create_engine, JSON, Boolean
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


class OperatorRecord(Record):
	__tablename__ = 'operators'

	name         : Mapped[str]             = mapped_column(String(255),                  primary_key=True, comment='Unique operator name')
	class_name   : Mapped[str]             = mapped_column(String(255),                  nullable=False,   comment='Unique operator class name')
	description  : Mapped[str]             = mapped_column(Text,                         nullable=True,    comment='Optional operator description')
	code         : Mapped[str]             = mapped_column(Text,                         nullable=True,    comment='Source code or prompt (or empty for composite)')
	restrict     : Mapped[bool]            = mapped_column(Boolean,                      default=True,     nullable=False, comment='If True, apply interpreter restrictions')
	
	input_type   : Mapped[Dict[str, Any]]  = mapped_column(JSON,                         nullable=False,   comment='Full JSON Schema')
	output_type  : Mapped[Dict[str, Any]]  = mapped_column(JSON,                         nullable=False,   comment='Full JSON Schema')

	scope        : Mapped[Dict[str, Any]]  = mapped_column(MutableDict.as_mutable(JSON), default=dict,     comment='Runtime scope for function operators')
	config       : Mapped[Dict[str, Any]]  = mapped_column(MutableDict.as_mutable(JSON), default=dict,     comment='Configuration passed to interpreter')
