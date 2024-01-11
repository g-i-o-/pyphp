from .parser import *
from .compiler import *
from .phpbuiltins import *
from .prepr import *
from .phpclass import *
from .phpfunction import *
from .phparray import *
from .coerce import *
from .varref import VarRef, VarDef
from .errors import ExecuteError, ReturnError, StopExecutionError
import trace
import sys
from .scope import scope


# Verbosity levels for this module
VERBOSITY_NONE = 0
VERBOSITY_NOTIFY_RUNNING           = 1
VERBOSITY_SHOW_DEBUG               = 2
VERBOSITY_SHOW_FN_CALLS            = 3
VERBOSITY_SHOW_VISITED_NODES       = 4
# current verbosity level
VERBOSE = VERBOSITY_NONE



class AbstractPhpExecuter(object):
	
	def __init__(self, code_tree, initial_scope=None, 
		stdout=None, stderr=None, stdin=None):
		self.code_tree = code_tree
		self.filename = code_tree.filename
		self.globals = self.make_global_scope(initial_scope)
		self.ERROR_REPORTING = constants.E_ALL
		self.last_node  = None
		self.last_scope = None
		self.pipe_stdout = stdout if stdout else sys.stdout
		self.pipe_stderr = stderr if stderr else sys.stderr
		self.pipe_stdin = stdin if stdin else sys.stdin
	
		if VERBOSE >= VERBOSITY_SHOW_VISITED_NODES:
			trace.trace_obj_calls(self, ['!', 'visit', 'get_val', 'report_error'], 'args')
	
	error_prefixes = dict([(getattr(constants, k), (v, sev)) for v, ks, sev in (
		('Fatal error' , ['E_CORE_ERROR', 'E_ERROR', 'E_USER_ERROR', 'E_COMPILE_ERROR'], 2),
		('Warning'     , ['E_CORE_WARNING', 'E_WARNING', 'E_USER_WARNING', 'E_COMPILE_WARNING'], 0),
		('Parse error' , ['E_PARSE'], 0),
		('Notice'      , ['E_NOTICE', 'E_USER_NOTICE'], 0),
		('Strict Standards' , ['E_STRICT'], 0),
		('Catchable fatal error' , ['E_RECOVERABLE_ERROR'], 1),
		('Deprecated'  , ['E_DEPRECATED', 'E_USER_DEPRECATED'], 0)
	) for k in ks])
	
	def report_error(self, err_type, msg):
		prefix, severity = self.error_prefixes.get(err_type, 'Error')
		if (err_type & self.ERROR_REPORTING) != 0:
			print ("\n%s: %s"%(prefix, msg))
		if severity > 0:
			raise StopExecutionError("\n%s: %s"%(prefix, msg))
			
	
	def make_global_scope(self, initial_scope=None):
		if initial_scope is None:
			initial_scope = {}
		global_scope = {
			'$_SERVER' : phparray.PHPArray(
				('SCRIPT_NAME', self.filename)
			),
			'$_GET' : phparray.PHPArray(),
			'$_POST' : phparray.PHPArray(),
			'$_FILES' : phparray.PHPArray()
		}
		global_scope.update(initial_scope)
		return scope(global_scope, {'%executer':self}, builtins, name='global')
		
	def __call__(self):
		return self.execute()
		
	def execute(self):
		if VERBOSE >= VERBOSITY_NOTIFY_RUNNING:
			print ("Running %r\n\n---\n"%self.code_tree)
		try:
			return self.visit(self.code_tree, self.globals)
		except StopExecutionError as e:
			if self.last_node:
				print (self.last_node.prepr())
				print (self.last_scope.prepr())
		except Exception as e:
			if self.last_node:
				print ("Error ocurred in %s (line %s)"%(self.last_node.filename, self.last_node.line_num))
				print (self.last_node.prepr())
				print (self.last_scope.prepr())
			raise
		
	def visit(self, tree_node, local_dict):
		last_context = self.last_node, self.last_scope
		self.last_node, self.last_scope  = tree_node, local_dict
		if VERBOSE >= VERBOSITY_SHOW_VISITED_NODES:
			print ("Visiting %s (line %s) : %s %s"%(tree_node.filename, tree_node.line_num, tree_node.name, prepr.prepr(local_dict)))
		fn = getattr(self, 'exec_%s'%tree_node.name, None)
		if fn is not None:
			retval = fn(tree_node, local_dict)
		else:
			retval = self.visit_default(tree_node, local_dict)
		self.last_node, self.last_scope = last_context
		return retval
	def visit_default(self, tree_node, local_dict=None):
		if VERBOSE >= VERBOSITY_SHOW_DEBUG:
			print (tree_node.prepr())
		raise ExecuteError("Cannot visit node %r, visitor method 'exec_%s' not found.\n"%(tree_node.name, tree_node.name))

	def has_val(self, var_ref):
		if isinstance(var_ref, VarRef):
			return var_ref.isset()
		else:
			return True
	
	def get_val(self, var_ref):
		if isinstance(var_ref, VarRef):
			return var_ref.get()
		else:
			return var_ref
		
	def set_val(self, var_ref, value):
		if isinstance(var_ref, VarRef):
			return var_ref.set(value)
		else:
			raise ExecuteError("Cannot assign %r to %r"%(var_ref, value))

class PhpExecuter(AbstractPhpExecuter):
	def exec_php_file(self, node, local):
		rv = None
		for child in node.children:
			rv = self.visit(child, local)
		return rv

	def exec_stmt_block(self, node, local):
		rv = None
		for child in node.children:
			rv = self.visit(child, local)
		return rv
	
	def exec_echo(self, node, local):
		echo_args = [self.get_val(self.visit(subnode, local)) for subnode in node.children]
		self.pipe_stdout.write(''.join(echo_args))
		return 1
	
	exec_print_expression = exec_echo
	
	def exec_define(self, node, local):
		args = [self.visit(i, local) for i in node.children]
		self.globals[args[0]] = self.get_val(args[1])
		
	def exec_assignment_expression(self, node, local):
		child_len = len(node.children)
		rhs_value = self.get_val(self.visit(node.children[ child_len-1 ], local))
		lhs_idx = child_len - 2
		while lhs_idx >= 0:
			op_node = node.children[ lhs_idx ]
			assign_op = op_node.name
			lhs_var_ref = self.visit(op_node.children[0], local)
			self.set_val(lhs_var_ref, rhs_value)
			lhs_idx -= 1
		return rhs_value


	def exec_bit_and_expression(self, node, local):
		val = -1
		for subnode in node.children:
			if subnode.name == '&':
				subnode = subnode.children[0]
			val &= coerce.to_int(self.get_val(self.visit(subnode, local)))
		return val
	
	def exec_bit_or_expression(self, node, local):
		val = 0
		for subnode in node.children:
			val |= int(self.get_val(self.visit(subnode, local)))
		return val
	
	def exec_bit_or_expression(self, node, local):
		val = 0
		for subnode in node.children:
			val ^= int(self.get_val(self.visit(subnode, local)))
		return val
	
	#def exec_bitshift_expression(self, node, local):
	#	num = int(self.get_val(self.visit(subnode, local)))
	#	num, bits = [int(self.get_val(self.visit(subnode, local))) for subnode in node.children[:2]]
	#	return num << 
	
	#def exec_expression_list(self, node, local):
	#	pass
	#def exec_for_stmt(self, node, local):
	#	pass
	#def exec_foreach_stmt(self, node, local):
	#	pass
	def exec_return_stmt(self, node, local):
		raise ReturnError(self.visit(node.children[0], local) if len(node.children) > 0 else None)
	#def exec_term_expression(self, node, local):
	#	pass
	#def exec_typecheck(self, node, local):
	#	pass
	
	def exec_if(self, node, local):
		condition = self.visit(node.children[0], local)
		if condition:
			return self.visit(node.children[1], local)
		elif len(node.children) > 2:
			return self.visit(node.children[2], local)
	
	def exec_eq_comp_expression(self, node, local):
		val=None
		for i, subnode in enumerate(node.children):
			if not i :
				val = self.get_val(self.visit(subnode, local))
			else :
				op = subnode.name
				val2 = self.get_val(self.visit(subnode.children[0], local))
				if op == '==':
					val = (val2 == val)
				elif op in ('!=', '<>'):
					val = (val2 != val)
				elif op == '===':
					val = (val2 is val)
				elif op == '!==':
					val = not (val2 is val)
		return val
	
	def exec_order_comp_expression(self, node, local):
		val=None
		for i, subnode in enumerate(node.children):
			if not i :
				val = self.get_val(self.visit(subnode, local))
			else :
				op = subnode.name
				val2 = self.get_val(self.visit(subnode.children[0], local))
				if op == '<':
					val = (val < val2)
				elif op in ('<='):
					val = (val <= val2)
				elif op == '>':
					val = (val > val2)
				elif op == '>=':
					val = (val >= val2)
		return val

	def exec_direct_output(self, node, local):
		self.pipe_stdout.write(node.children[0])
		
	def exec_primitive(self, node, local):
		subnode = node.children[0]
		if isinstance(subnode, Token):
			token = subnode
			if token[0] in (TOKEN_STRING, TOKEN_NUMBER):
				return token[1]
			elif token[0] == TOKEN_IDENTIFIER:
				lcaseid = token[1].lower()
				if lcaseid in primitives:
					return primitives[lcaseid]
				else:
					return VarRef(token[1], self, local)
			elif token[0] == TOKEN_VARIABLE:
				# print ("Var Ref %r on %r with %r"%(token[1], self, local.prepr()))
				return VarRef(token[1], self, local)
			elif token[0] == TOKEN_INTERPOLATED_STRING:
				text = ''.join([coerce.to_string(self.get_val(self.visit(x, local)) if isinstance(x, TreeNode) else x) for x in token[1]])
				return text
		elif isinstance(subnode, TreeNode):
			return self.visit(subnode, local)
		raise ExecuteError("invalid primitive %r"%subnode)
	
	def exec_array_literal(self, node, local):
		elements = [self.visit(subnode, local) for subnode in node.children]
		return phparray.PHPArray(*elements)
	
	def exec_array_element(self, node, local):
		if len(node.children) > 1:
			key, value = [self.get_val(self.visit(subnode, local)) for subnode in node.children[:2]]
		else:
			key, value = None, self.get_val(self.visit(node.children[0], local))
		return key, value
	
	def exec_member_expression(self, node, local):
		subnode = node.children[0]
		if isinstance(subnode, Token):
			token = subnode
			if token[0] == (TOKEN_VARIABLE, TOKEN_IDENTIFIER):
				return VarRef(token[1], self, local, '->')
		else:
			return self.visit(subnode)
	
	def exec_followed_primitive(self, node, local):
		fprimitive = self.visit(node.children[0], local)
		
		# print factor, node, local
		for f_idx in range(1, len(node.children)):
			# print fprimitive, node.children[f_idx]
			fprimitive = self.apply_follower(fprimitive, node.children[f_idx], local)
			
		return fprimitive
	
	def exec_negated(self, node, local):
		# print node.prepr()
		val = self.get_val(self.visit(node.children[0], local))
		# print val, not val
		return not val
	
	def exec_factor(self, node, local):
		unaries = node.children[0]
		if unaries.name != "unary_op":
			unaries = None
			
		old_reporting = self.ERROR_REPORTING
		if unary_idx is not None and '@' in unaries.children:
			self.ERROR_REPORTING = 0
		
		factor = self.visit(node.children[0 if unaries is None else 1], local)
		
		# print factor
		if unary_idx is not None:
			for unary in node.children[0].children:
				self.apply_unary(factor, unary)
				
		self.ERROR_REPORTING = old_reporting
		return factor

	def exec_classdef(self, node, local):
		print ("%"*100)
		cls_name, scls_name, body = node.children
		if scls_name and not scls_name[1] in local:
			raise ExecuteError("Undefined superclass %s"%scls_name[1])
		class_context = scope({}, local, name=cls_name[1])
		if body:
			body = self.visit(body, class_context)
		defined_class = PHPClass(cls_name[1], local[scls_name[1]] if scls_name else None, body, class_context, filename=node.filename, line_num=node.line_num)
		#print ("class %s defined"%defined_class)
		#print ("%"*100)
		self.globals[defined_class.name] = defined_class
		return defined_class
	
	def exec_classdef_block(self, node, local):
		members = [
			self.visit(member, local) for member in node.children
		]
		return members

	def exec_vardef_stmt(self, node, local):
		if len(node.children) == 2:
			modifiers, name = node.children
			initval = None
		else:
			modifiers, name, initval = node.children
		if initval:
			initval = self.get_val(self.visit(initval, local))
		# print name
		return VarDef(name[1], modifiers, initval)
	
	def exec_conditional_expression(self, node, local):
		condition, true_block, false_block = node.children[:3]
		if self.get_val(self.visit(condition, local)):
			return self.visit(true_block, local)
		else:
			return self.visit(false_block, local)

	
	def exec_const_vardef_stmt(self, node, local):
		name = node.children[0][1]
		val  = self.get_val(self.visit(node.children[1], local)) if len(node.children) > 1 else None
		return VarDef(name, ['const'], val)

	def exec_funcdef(self, node, local):
		name, params, body = node.children
		fn = PHPFunction(name[1], None, self.visit(params, local), body, filename=node.filename, line_num=node.line_num)
		fn.context = self.globals
		#print ("Defined function ::: %r"%fn)
		self.globals[name[1]] = fn
		# print local
		return fn

	def exec_methoddef(self, node, local):
		modifiers, name, params, body = node.children
		return PHPFunction(name[1], modifiers, self.visit(params, local), body, filename=node.filename, line_num=node.line_num)
	
	def exec_parameter_list(self, node, local):
		return [self.visit(subnode, local) for subnode in node.children]
	
	def exec_parameter(self, node, local):
		hint, param, default = node.children
		if hint:
			hint = hint[1]
		has_default = False
		if default:
			has_default = True
			default = self.get_val(self.visit(default, local))
		param = [hint, param[1]]
		if has_default:
			param.append(default)
		return param
	
	def exec_and_expression(self, node, local):
		for subnode in node.children:
			if subnode.name in ('&&', 'and'):
				subnode = subnode.children[0]
			val = self.get_val(self.visit(subnode, local))
			if not val:
				return False
		return val
	
	exec_sym_and_expression = exec_and_expression
	
	def exec_or_expression(self, node, local):
		# print node.prepr()
		for i, subnode in enumerate(node.children):
			print (subnode)
			val = self.get_val(self.visit(subnode.children[0] if i else subnode, local))
			if val:
				return val
		return False
	
	exec_sym_or_expression = exec_or_expression
	
	def exec_xor_expression(self, node, local):
		lval = False
		for subnode in node.children:
			val = self.get_val(self.visit(subnode, local))
			lval = (val and not lval) or (lval and not val)
		return lval
	
	def apply_follower(self, factor, follower, local):
		# print follower
		follower_fn = "apply_%s_follower"%follower.name
		if hasattr(self, follower_fn):
			return getattr(self, follower_fn)(factor, follower, local)
		else:
			raise ExecuteError("Unknown follower for %s."%follower.prepr())
		
	def apply_unary(self, factor, unary):
		# ('!', '~' , '++', '--', '+', '-', '@')
		if unary == '!':
			factor = not self.get_val(factor)
		elif unary == '~':
			factor = ~ self.get_val(factor)
		elif unary == '+':
			factor = self.get_val(factor)
		elif unary == '-':
			factor = self.get_val(factor)
		elif unary == '++':
			fval = self.get_val(factor)
			self.set_val(factor, fval + 1)
			factor = self.get_val(factor)
		elif unary == '--':
			fval = self.get_val(factor)
			self.set_val(factor, fval - 1)
			factor = self.get_val(factor)
		return factor
		
	def apply_array_indexing_follower(self, factor, follower, local):
		index = self.get_val(self.visit(follower.children[0], local))
		if isinstance(factor, VarRef):
			return factor[index]
		else:
			raise ExecuteError("Cannot index %r "%factor)
	def apply_fncall_follower(self, factor, follower, local):
		if VERBOSE >= VERBOSITY_SHOW_FN_CALLS:
			print ("Calling %s\n on %s"%(follower.prepr(), factor))
		
		func_name=factor
		factor = self.get_val(factor)
		if type(factor) is str:
			func_name = factor
			if factor in self.globals:
				factor = self.globals[factor]
			else:
				raise ExecuteError("Function %s does not exists", factor)
		
		if factor is None:
			if isinstance(func_name, VarRef):
				func_name = func_name.qualified_name()
			func_type = 'method' if '::' in func_name or '->' in func_name else 'function'
			self.report_error(constants.E_ERROR, 'Call to undefined %s %s() in %s on line %d'%(func_type, func_name, follower.filename, follower.line_num))
			raise ExecuteError("null is not callable.")
		elif isinstance(factor, builtin):
			args = [ self.visit(x, local) for x in follower.children[0].children]
			if VERBOSE >= VERBOSITY_SHOW_FN_CALLS:
				print ("calling builtin %r with %r"%(factor, args))
			retval = factor(args, self, local)
		else:
			args = [ self.get_val(self.visit(x, local)) for x in follower.children[0].children]
			if VERBOSE >= VERBOSITY_SHOW_FN_CALLS:
				print ("calling %r with %r"%(factor, args))
			retval = factor(*args, filename=follower.filename, line_num=follower.line_num)
		# print ("Return value : ", retval)
		return retval

	def apply_static_member_access_follower(self, factor, follower, local):
		subnode = follower.children[0].children[0]
		if isinstance(subnode, Token):
			member_name = subnode[1]
		else:
			member_name = self.get_val(self.visit(subnode, local))
		if isinstance(factor, VarRef):
			return factor.getitem(member_name, '::')
		else:
			return factor[member_name]

	def exec_add_expression(self, node, local):
		# print node.prepr()
		value = None
		for i, child in enumerate(node.children):
			if i > 0:
				op = child.name
				arg = self.get_val(self.visit(child.children[0], local))
				if op == '.':
					value = coerce.to_string(value) + coerce.to_string(arg)
				elif op == '+':
					val_is_array = isinstance(value, phparray.PHPArray)
					arg_is_array = isinstance(arg, phparray.PHPArray)
					if val_is_array or arg_is_array:
						if val_is_array and arg_is_array:
							value = value + arg
						else:
							self.report_error(constants.E_ERROR, 'Unsupported operand types in %s on line %d'%(child.filename, child.line_num))
					else:
						value = self.coerce_numeric(value) + self.coerce_numeric(arg)
				elif op == '-':
					value = self.coerce_numeric(value) - self.coerce_numeric(arg)
			else:
				value = self.get_val(self.visit(child, local))
		return value
	
	def coerce_numeric(self, x):
		if type(x) in (int, long, float):
			return x
		elif type(x) in (str, unicode) :
			m = RE_float.match(x)
			if m:
				return float(m.group(0))
			m = RE_number.match(x)
			if m:
				return int(m.group(0))
		return 0

def execute_file(phpfile, global_dict=None, **kwargs):
	if type(phpfile) is str:
		phpfile = parse_file(phpfile)
	if isinstance(phpfile, TokenList):
		phpfile = compile_php(phpfile)
	return execute_php(phpfile, global_dict, **kwargs)
	

def execute_php(phpcode, global_dict=None, **kwargs):
	if type(phpcode) is str:
		phpcode = parse_php(phpcode)
	if isinstance(phpcode, TokenList):
		phpcode = compile_php(phpcode)
	if not isinstance(phpcode, TreeNode):
		raise ArgumentError("Given argument is not php code %r"%phpcode)
	E = PhpExecuter(phpcode, global_dict, **kwargs)
	E.execute()
	return E
	

if __name__ == '__main__':
	import sys
	# print sys.argv
	show_globals = False
	phpfile=None
	phpargv=[]
	if len(sys.argv) > 1:
		for arg in sys.argv[1:]:
			if phpfile is None and len(arg) > 3 and arg[0:2] == '--':
				comps = arg[2:].split('=', 1)
				key = comps[0]
				val = comps[1] if len(comps) > 1 else 1
				if key == 'show_globals' and int(val):
					show_globals = True
				else:
					print ("Unknown option %s"%arg)
			else:
				if len(phpargv) == 0:
					phpfile = arg
				phpargv.append(arg)
				
	init_scope = {
		'argv' : phpargv,
		'argc' : len(phpargv)
	}
	
	if phpfile:
		executer = execute_file(phpfile, init_scope)
	else :
		executer = execute_php(TEST_CODE)
		
	if show_globals:
		print ("[ended]\n-- globals --")
		for i in executer.globals.dict:
			print ("%-14s  ->  %r"%(i, executer.globals[i]))
