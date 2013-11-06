import errors
import executer
from phpbuiltins import PHP_CONSTANTS
from scope import scope


class PHPFunction():
	def __init__(self, name, modifiers, params, body, context = None, filename = None, line_num = 0):
		self.name = name
		self.modifiers = modifiers
		self.params    = params
		self.body      = body
		self.context   = context
		self.filename  = filename
		self.line_num  = line_num
	def __repr__(self):
		return '<phpfunction %s(%s) defined in %s on line %d>'%(self.name, ', '.join([
			'%s%s%s'%('%s '%x[0] if x[0] else '', x[1], ' = %r'%x[2] if len(x) > 2 else '')
			for x in self.params
		]), self.filename, self.line_num)
	def __call__(self, *args, **kwargs):
		if 'context' in kwargs:
			context = kwargs['context']
		else:
			context = self.context
			
		caller_filename = kwargs['filename'] if 'filename' in kwargs else None
		caller_line_num = kwargs['line_num'] if 'line_num' in kwargs else None
		
		
		# print "Calling %r with %r"%(self, args)
		call_context = scope({
			'%func_args' : args,
			'__FUNCTION__' : self.name
		}, self.context)
		
		
		executer = call_context['%executer']
		
		arglen = len(args)
		for i, par in enumerate(self.params):
			if i < arglen:
				val = args[i]
			elif len(par) > 2:
				val = par[2]
			else:
				val = None
				executer.report_error(
					PHP_CONSTANTS['E_WARNING'],
					"Missing argument %d for %s()%s defined in %s on line %d"%(i+1, self.name,
						', called in %s on line %d and'%(caller_filename, caller_line_num) if caller_filename is not None and caller_line_num is not None else '',
						self.filename, self.line_num)
					# "Warning: Missing argument 2 for f(), called in /Users/giovanyvega/langdev/php/test/err_func_missing_arg.php on line 7 and defined in /Users/giovanyvega/langdev/php/test/err_func_missing_arg.php on line 3"
				)
				# raise errors.ExecuteError("Missing required argument %d for %r"%(i, self))
			
			call_context[par[1]] = val
			
		# print executer
		# print self.body
		# print call_context
		
		executer.visit(self.body, call_context)
		
		# raise errors.ExecuteError("Can't execute yet.")
	
	def is_static(self):
		return 'static' in self.modifiers

	def bind(self, context):
		self.context = context
		return self