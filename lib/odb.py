from sqlalchemy.orm import Session
from .transform     import T


class ODB:

	# Magic
	################################################################################################

	def __init__(self, session: Session, instance: 'O'):
		self._session  = session
		self._instance = instance
		self._model    = type(instance)
		self._table    = T(T.PYDANTIC, T.SQLALCHEMY_TABLE, self._model)

	def __getattr__(self, name): return getattr(self._session, name)

	# Private
	################################################################################################

	def _o_or_none(self, obj): return obj if obj is None or isinstance(obj, self._model) else None

	# Public
	################################################################################################

	def create_table(self)          : self._table.create(self._session.bind, checkfirst=True)
	def drop_table(self)            : self._table.drop(self._session.bind, checkfirst=True)
	def query(self)                 : return self._session.query(self._model)

	def filter(self, *args)         : return self.query().filter(*args)
	def get(self, id)               : return self._o_or_none(self._session.get(self._model, id))
	def first(self)                 : return self._o_or_none(self.query().first())
	def count(self)                 : return self.query().count()
	def exists(self)                : return self.query().exists().scalar()
	def all(self)                   : return [r for r in self.query().all() if isinstance(r, self._model)]

	def update(self, where, values) : self.query().filter(where).update(values); self.commit()
	def delete(self, *args)         : self.query().filter(*args).delete();       self.commit()

	def refresh(self, obj=None)     : self._session.refresh(obj or self._instance)
	def expunge(self, obj=None)     : self._session.expunge(obj or self._instance)
	def add(self, obj=None)         : self._session.add(obj     or self._instance)
	def save(self, obj=None)        : self.add(obj);       self.commit()
	def commit(self)                : self.create_table(); self._session.commit()
	def rollback(self)              : self._session.rollback()
	def flush(self)                 : self._session.flush()
	def close(self)                 : self._session.close()
