import varref
import errors

class PHPClass:
	def __init__(self, name, superclass, body, context, filename=None, line_num=0):
		self.name = name
		self.superclass = superclass
		self.body = dict([(member.name, member) for member in body]) if body else {}
		self.context = context
		self.context['self'] = self
		self.context['parent'] = superclass
		self.filename = filename
		self.line_num = line_num
		# print self.body, self.context
		
	def __contains__(self, key):
		return key in self.body
		
	def __getitem__(self, key):
		if key in self.body:
			member = self.body[key]
			if not member.is_static():
				raise errors.ExecuteError("Fetching non-static member %r from %r."%(member, self))
			return member.bind(self.context)
		else:
			if self.superclass:
				return self.superclass[key]
			else:
				return null
			
	def __setitem__(self, key, value):
		# print self
		# print key
		# print value
		self.body[key] = value
		
	def __call__(self, *args):
		print "Called %s with %r"%(self, args)
		print qqwweerr
		
	def __repr__(self):
		return '<phpclass %r%s>'%(self.name, ' extends %r'%self.superclass.name if self.superclass else '')