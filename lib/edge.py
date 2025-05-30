from typing  import Any, Optional
from dapi.db import EdgeRecord


class Edge:
	@property
	def model(self):
		return EdgeRecord

	def __init__(self, session):
		self.session = session

	def create(self, **kwargs):
		kwargs = {k: (v if v is not None else '') for k, v in kwargs.items()}
		edge = EdgeRecord(**kwargs)
		self.session.add(edge)
		self.session.commit()
		return edge

	# def remove_for(self, obj: Any):
	# 	self.session.query(EdgeRecord).filter(
	# 		(EdgeRecord.id1 == obj.id) | (EdgeRecord.id2 == obj.id)
	# 	).delete()
	# 	self.session.commit()

	def get_edges(self, obj: Any, rel: str = None):
		query = self.session.query(EdgeRecord).filter(
			(EdgeRecord.id1 == obj.id) | (EdgeRecord.id2 == obj.id)
		)
		if rel is not None:
			query = query.filter(
				(EdgeRecord.rel1 == rel) | (EdgeRecord.rel2 == rel)
			)
		return query.all()

	# def replace_all(self, obj: Any, rel: str, new_ids: list[int], type2: str):
	# 	self.session.query(EdgeRecord).filter(
	# 		EdgeRecord.id1  == obj.id,
	# 		EdgeRecord.rel1 == rel
	# 	).delete()
	# 	for index, id2 in enumerate(new_ids):
	# 		self.create(
	# 			id1   = obj.id,
	# 			type1 = obj.__class__.__name__,
	# 			id2   = id2,
	# 			type2 = type2,
	# 			rel1  = rel,
	# 			key1  = str(index),
	# 		)
	# 	self.session.commit()
