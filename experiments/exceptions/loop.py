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
		print('Resuming C with corrected value:', value)
		return check()

	def check():
		if value != 42:
			raise CorrectionRequired(f'Value {value} is not acceptable', resume)
		print('C completed successfully with', value)
		return value

	return check()

def B():
	return C()

def A():
	gen = B  # save function to call, because we'll need it repeatedly
	while True:
		try:
			result = gen()
			print('Final result from C:', result)
			break
		except CorrectionRequired as e:
			while True:
				try:
					corrected_value = int(input('Enter corrected value: '))
					result = e.resume_callback(corrected_value)
					break  # Break inner loop if correction was accepted
				except CorrectionRequired as e2:
					print('Still not good:', e2)
					e = e2  # update current exception for the next correction
A()
