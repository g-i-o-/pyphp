import phpbuiltins

VERBOSITY_NONE = 0
VERBOSITY_SHOW_DEBUG = 1

VERBOSE = VERBOSITY_NONE



class VarDef(object):
	def __init__(self, name, modifiers, default):
		self.name      = name
		self.modifiers = modifiers
		self.default   = default
	def __repr__(self):
		return "%s%s%s"%('%s '%(' '.join(self.modifiers) if self.modifiers else ''), self.name, ' = %s'%self.default if self.default else '')
	def is_static(self):
		return 'static' in self.modifiers

class VarRef(object):
	def __init__(self, name, executer, context=None):
		self.name = name
		self.executer = executer
		self.context = context
		
	def get_context_obj(self, auto_create=False):
		if VERBOSE >= VERBOSITY_SHOW_DEBUG:
			print "Getting context of %r"%self
		if isinstance(self.context, VarRef):
			# print "  -> context is chained to %r"%self.context
			ctx_name, ctx = self.context.get_context_obj()
			if self.context.name in ctx:
				ctx = ctx[self.context.name]
			elif auto_create:
				# print "Context does not exists in parent's context %r. Auto-creating %r"%(ctx, self.context.name)
				ctx[self.context.name] = {}
				# print "  --> %r"%ctx
				ctx = ctx[self.context.name]
			else:
				raise IndexError("Cannot get context of %r."%self)
			return self.context.name, ctx
		else:
			# print "  -> explicitly stated as %r"%self.context
			return "<implicit>", self.context
		
	def get(self):
		context_name, context = self.get_context_obj(True)
		# print "%r[%r] = %r"%(context, self.name, value)
		if self.name not in context:
			self.executer.report_error( phpbuiltins.PHP_CONSTANTS['E_WARNING'], "%s[%r] doesn't exist"%(context_name, self.name) )
			return None
		return context[self.name]
		
	def set(self, value):
		context_name, context = self.get_context_obj(True)
		# print "%r[%r] = %r"%(context, self.name, value)
		context[self.name] = value
	
	def __getitem__(self, index):
		return VarRef(index, self.executer, self)
	
	def __repr__(self):
		return "%s(%r, %r)"%(self.__class__.__name__, self.name, self.context)
