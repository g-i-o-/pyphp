import phpbuiltins.constants

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
		return 'static' in self.modifiers or 'const' in self.modifiers

class VarRef(object):
	def __init__(self, name, executer, context, particle=''):
		self.name = name
		self.particle = particle
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
		elif isinstance(self.context, VarDef):
			return self.context.name, self.context.default
		else:
			# print "  -> explicitly stated as %r"%self.context
			return "<implicit>", self.context
		
	def get(self):
		context_name, context = self.get_context_obj(True)
		# print "varref context %r[%r]"%(context, self.name)
		if self.name not in context:
			self.executer.report_error( phpbuiltins.constants.E_WARNING, "%s doesn't exist"%(self.qualified_name()) )
			return None
		value = context[self.name]
		if isinstance(value, VarDef):
			value = value.default
		return value;
		
	def set(self, value):
		context_name, context = self.get_context_obj(True)
		# print "%r[%r] = %r"%(context, self.name, value)
		context[self.name] = value
		
	def isset(self):
		import prepr
		try:
			#print "Fetching varref context..."
			context_name, context = self.get_context_obj(False)
			#print "  => ", context
		except IndexError, ie:
			#print "  => context not found!!!"
			return False
		#print "  => var %r in context ::"%self.name, self.name in context
		if self.name not in context:
			#print "  => var %r not in context!!"%self.name
			return False
		return True;
	
	
	def __getitem__(self, index):
		return VarRef(index, self.executer, self, '[')
	
	def getitem(self, index, particle='['):
		return VarRef(index, self.executer, self, particle)
	
	
	def __repr__(self):
		return "%s(%r, %r)"%(self.__class__.__name__, self.name, self.context)
	
	def prepr(self, *args):
		return self.qualified_name()
	

	def qualified_name(self):
		import phpclass
		name_parts = []
		if self.particle == '[':
			name_parts.append(']')
		if isinstance(self.name, VarRef):
			if self.particle != '[':
				name_parts.append('}')
			name_parts.append(self.name.qualified_name())
			if self.particle != '[':
				name_parts.append('{')
		else:
			name_parts.append(self.name)
		name_parts.append(self.particle)
		ctx = self.context
		while ctx:
			if isinstance(ctx, VarRef):
				if ctx.particle == '[':
					name_parts.append(']')
				if isinstance(ctx.name, VarRef):
					if ctx.particle != '[':
						name_parts.append('}')
					name_parts.append(ctx.name.qualified_name())
					if ctx.particle != '[':
						name_parts.append('{')
				else:
					name_parts.append(ctx.name)
				name_parts.append(ctx.particle)
				ctx = ctx.context
			elif isinstance(ctx, phpclass.PHPClass):
				name_parts.append(ctx.name)
				ctx = None
			else:
				ctx = None
		# print '\n'*5, '\n\n'.join(['%d=>%r'%(i,x) for i,x in enumerate(name_parts)]), '\n'*5
		return ''.join(list(reversed(name_parts)))
