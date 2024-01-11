"""
Declares a @builtin decorator class for tagging php built-in functions, as well as implements and exports most if not all php built-in functions.
"""

import pyphp.scope as scope

from .builtin import *
from .string import *
from .regex import *
from .constants import *
from .datetime import *
from .lang import *
from .primitives import *

def gen_builtins():
	modules=[constants, datetime, lang, string, regex]
	for module in modules:
		for member_name in dir(module):
			member = getattr(module, member_name)
			if member_name == 'CONSTANTS':
				for k,v in member:
					yield (k, v)
			elif isinstance(member, builtin):
				yield(member_name, member)
		



builtins = scope.scope(
	dict(x for x in gen_builtins()),
	name='phpbuiltins'
)
