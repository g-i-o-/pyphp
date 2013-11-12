"""
Declares a @builtin decorator class for tagging php built-in functions.
"""

class builtin(object):
	"Class for tagging built in functions"
	def __init__(self, func):
		self.func = func
	def __call__(self, *args, **kw):
		return self.func(*args, **kw)
	def __repr__(self):
		return "<php-builtin-function %r>"%self.func.__name__
