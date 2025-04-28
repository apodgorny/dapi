class CorrectionRequired(Exception):
	def __init__(self, message, resume_callback):
		super().__init__(message)
		self.resume_callback = resume_callback

def C():
	print('Start C')
	value = 10

	def resume(new_value):
		nonlocal value
		value = new_value
		print('Continuing C with corrected value:', value)

	if value == 10:
		raise CorrectionRequired('Bad value', resume)

	print('C completed with', value)

def B():
	C()

def A():
	try:
		B()
	except CorrectionRequired as e:
		print('Caught correction request:', e)
		e.resume_callback(42)

A()
