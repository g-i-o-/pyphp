"""
Class emulating a php array.
php arrays have semantic properties that differ from normal python objects.
PHP arrays are:
	associative (keys can be numbers or strings)
	elements are iterated on the insertion order of their keys
	numeric keys are casted to integers
	appended items are assigned a numeric key corresponding to the maximum of the numeric keys plus 1
	string keys of numeric integers are casted to integers
	an internal iterator index is associated to the array and manipulated through php built-in functions
	they are passed by reference, with a copy on write policy

"""

class PHPArray:
	"Class that emulates a php array"
	def __init__(self, *args):
		self.keys  = []
		self.dict  = {}
		self.max_i = 0
		
		for k, v in args:
			self[k] = v
			
	@staticmethod
	def _is_numerable(k):
		if type(k) in (float, int):
			return True
		else:
			k = str(k)
			if k[0] in '0123456789-':
				for c in k[1:]:
					if c not in '0123456789':
						return False
				return True
			else:
				return False
			
	def _coerce_key_(self, k, for_insertion = True):
		if k is None:
			if for_insertion:
				k = self.max_i
				self.max_i += 1
		elif self._is_numerable(k):
			k = int(k)
			if for_insertion:
				self.max_i = k
		return k
		
	def __setitem__(self, k, v):
		k = self._coerce_key_(k, True)					
		if not k in self.dict:
			self.keys.append(k)		
		self.dict[k] = v
	
	def __getitem__(self, k):
		return self.dict[k]
	
	def __contains__(self, k):
		return k in self.dict
	
	def __len__(self):
		return len(self.keys)
	
	def __iter__(self):
		return iter(self.keys)
	
	def push(self, *items):
		for item in items:
			key = self.max_i
			self.max_i += 1
			self.keys.append(key)
			self.dict[key] = item
		
	def pop(self):
		if len(self.keys) == 0:
			return None
		last_key = self.keys.pop(-1)
		self.dict.pop(last_key)
		self.max_i = max([0] + [x for x in self.keys if type(x) == int])
	
	def _gen_newkeys(self, start_i=0):
		i, kl, d = start_i, self.keys, self.dict
		for k in kl:
			v = d[k]
			if self._is_numerable(k):
				yield i, v
				i += 1
			else:
				yield k, v
		self.max_i = i
	
	def shift(self):
		if len(self.keys) == 0:
			return None
		
		self.keys.pop(0)
		
		new_kv_pair = [kv for kv in self._gen_newkeys()]
		self.dict = dict(new_kv_pair)
		self.keys = [k for k,v in new_kv_pair]
	
	def unshift(self, *items):
		new_kv_pair = [kv for kv in self._gen_newkeys(len(items))]
		self.dict = dict(new_kv_pair)
		for i, item in enumerate(items):
			self.dict[i] = item
		self.keys = range(len(items)) + [k for k,v in new_kv_pair]
	
	def __repr__(self):
		return 'phparray(%s)'%(', '.join([
			'%r=>%r'%(k, self.dict[k])
			for k in self.keys
		]))