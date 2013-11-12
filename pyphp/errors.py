class ExecuteError(StandardError):
	pass

class ReturnError(StandardError):
	def __init__(self, retval):
		self.retval = retval
	
