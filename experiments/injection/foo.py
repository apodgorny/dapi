
from data import data
globals().update(data)

class Foo:
	@staticmethod
	def haha(s):
		print(s, injected)