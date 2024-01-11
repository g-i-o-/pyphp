class ExecuteError(Exception):
	pass

class StopExecutionError(ExecuteError):
	def __init__(self, exitval=0):
		self.exitval = exitval


class ReturnError(Exception):
	def __init__(self, retval):
		self.retval = retval
	
