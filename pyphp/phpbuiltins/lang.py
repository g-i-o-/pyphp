"""
Language-related builtin functions.
   isset
   defined
   require(s)
   error_reporting
"""

from builtin import builtin
import errors


@builtin
def isset(args, executer, local_dict):
	er = executer.ERROR_REPORTING
	executer.ERROR_REPORTING=0
	try:
		for a in args:
			executer.get_val(a)
		val_set = True
	except:
		val_set = False
	
	executer.ERROR_REPORTING=er
	return val_set


@builtin
def defined(args, executer, local_dict):
	import phpfunction
	name = executer.get_val(args[0])
	if name[0] != '$' and name in local_dict:
		val = local_dict[name]
		if not val or not isinstance(val, phpfunction.PHPFunction):
			return True
	return False

def include_impl(args, executer, local_dict, require=False, once=False):
	# print "include impl : args:%r, executer:%r, local_dict:%r, require:%r, once:%r"%(args, executer, local_dict, require, once)
	lf_key='~!loaded_files'
	path = executer.get_val(args[0])
	if lf_key not in executer.globals:
		# print " --> Creating executer.globals[%r]"%lf_key
		executer.globals[lf_key] = {}
	
	if once and path in executer.globals[lf_key]:
		# print " -once-> file is already included"
		pass
	else:
		import os.path
		if os.path.exists(path):
			# print " --> including file %r"%path
			import compiler
			executer.globals[lf_key][path] = True
			executer.visit(compiler.compile_file(path), local_dict)
		elif require:
			raise errors.ExecuteError("required file %s not found!"%path)
	

@builtin
def require_once(args, executer, local_dict):
	include_impl(args, executer, local_dict, True, True)
@builtin
def require(args, executer, local_dict):
	include_impl(args, executer, local_dict, True, False)
@builtin
def include_once(args, executer, local_dict):
	include_impl(args, executer, local_dict, False, True)
@builtin
def include(args, executer, local_dict):
	include_impl(args, executer, local_dict, False, False)

def var_dump_impl(x, depth=0):
	import phparray
	dstr = "  "*depth
	t = type(x)
	if x is None:
		print "%sNULL"%dstr
	elif t in (int, long):
		print "%sint(%d)"%(dstr, x)
	elif t == str:
		print "%sstring(%d) %r"%(dstr, len(x), x)
	elif isinstance(x, phparray.PHPArray):
		print "%sarray(%d) {"%(dstr, len(x))
		for y in x:
			print "%s  [%r]=>"%(dstr, y)
			var_dump_impl(x[y], depth + 1)
		print "%s}"%dstr
		
		
@builtin
def var_dump(args, executer, local):
	args = [executer.get_val(a) for a in args]
	for arg in args:
		var_dump_impl(arg)

@builtin
def ini_set(args, executer, local):
	pass

@builtin
def error_reporting(args, executer, local):
	if len(args) > 0:
		executer.ERROR_REPORTING = executer.get_val(args[0])
	return executer.ERROR_REPORTING
