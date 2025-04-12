def f(count):
	indent = '-' * count
	if count == 0:
		print(indent, count)
		return None
	else:
		f(count - 1)
		f(count - 1)
		print(indent, count)

f(3)
