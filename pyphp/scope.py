
class scope(object):
	"Represents a scope, a context in which variables and functions are defined and bound to."
	def __init__(self, d=None, *parents, **kwargs):
		"Creates a scope with a given dictionary and parents. A name argument can be given to name the scope."
		self.dict  = d if d else {}
		self.parents = [p for p in parents if p]
		self.name = kwargs['name'] if 'name' in kwargs else None			
	def __contains__(self, key):
		if key in self.dict:
			return True
		else:
			for ps in self.parents:
				if key in ps:
					return True
		return False
	def __getitem__(self, key):
		if key not in self.dict:
			for ps in self.parents:
				if key in ps:
					return ps[key]
		return self.dict[key]
	def __setitem__(self, key, val):
		self.dict[key] = val
	def __iter__(self):
		import itertools
		return itertools.chain(self.dict, *self.parents)
	def __repr__(self):
		return '%sscope(%r)%s'%(self.name + '-' if self.name else '', self.dict, ('-[%s]'%(''.join([repr(x) for x in self.parents]))) if self.parents else '')
