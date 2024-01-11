from .varref import *
from .prepr import prepr
from .phpfunction import PHPFunction
from .errors import *

class PHPClass:
	def __init__(self, name, superclass, body, context, filename=None, line_num=0):
		self.name = name
		self.superclass = superclass
		self.body = {}
		self.instance_body = []
		if body:
			for member in body:
				if isinstance(member, PHPFunction):
					if member.is_static():
						self.body[member.name] = member
					else:
						self.instance_body.append(member);
				elif isinstance(member, VarDef):
					if member.is_static():
						self.body[member.name] = member.default
					else:
						self.instance_body.append(member);
				else:
					raise ExecuteError("Invalid class member %r in definition of class %s"%(member, self.name))
		self.context = context
		self.context['self'] = self
		self.context['parent'] = superclass
		self.filename = filename
		self.line_num = line_num
		# print self.body, self.context
		
	def __contains__(self, key):
		return key in self.body
		
	def __getitem__(self, key):
		# print ("getting %s from %s"%(key, self.name))
		if key in self.body:
			member = self.body[key]
			# print ("   :: ", prepr(self.body, 7))
			# print ("   => ", prepr(member))
			if hasattr(member, 'is_static') and not member.is_static():
				raise ExecuteError("Fetching non-static member %r from %r."%(member, self))
			if hasattr(member, 'bind'):
				return member.bind(self.context)
			else:
				return member
		else:
			if self.superclass:
				return self.superclass[key]
			else:
				return null
			
	def __setitem__(self, key, value):
		# print self
		# print key
		# print value
		# print ("@"*160)
		# print ("#"*160)
		# print ("setting %s in %s to %s"%(key, self.name, value))
		# print ("@"*160)
		if key not in self.body:
			# print ("!!!!!!!!!!!!!!!"*160)
			raise ExecuteError("Cannot set %s on class %s"%(key, self.name))
		self.body[key] = value
		
	def __call__(self, *args):
		print ("Called %s with %r"%(self, args))
		print (qqwweerr)
		
	def __repr__(self):
		return '<phpclass %r%s>'%(self.name, ' extends %r'%self.superclass.name if self.superclass else '')