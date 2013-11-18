"""
  Utility functions for implementing PHP's automatic type coercion.
"""

import phparray

def to_string(x):
	if x is None:
		return ''
	elif isinstance(x, phparray.PHPArray):
		return 'Array'
	else:
		return str(x)


def to_int(x):
	if x in (None, True, False):
		return 1 if x else 0
	else:
		xt = type(x)
		if xt is int:
			return x
		elif xt in (long, float):
			return int(x)
		elif xt in (str, unicode):
			ord_0, ord_9 = ord('0'), ord('9')
			sign, val, base = 1, 0, 10
			if x[0] in '-+':
				if x[0] == '-':
					sign = -1
				x = x[1:]				
			for c in x:
				ord_c = ord(c)
				if ord_0 <= ord_c <= ord_9:
					digit = ord_c - ord_0
					val = val*base + digit
				else:
					break
			return sign * val
		else:
			return 0

def to_bool(x):
	if x is None:
		return False
	else:
		xt = type(x)
		if xt is bool:
			return x
		elif xt in (str, unicode):
			return len(x) > 0 and x != '0'
		elif isinstance(x, pyphp.phparrar.PHPArray):
			return len(x) > 0