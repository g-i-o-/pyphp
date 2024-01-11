"""
Language-related builtin functions.
   isset
   defined
   require(s)
   error_reporting
"""

from .builtin import builtin
import pyphp.errors
import sys
from pyphp.prepr import prepr

@builtin
def isset(args, executer, local_dict):
	er = executer.ERROR_REPORTING
	executer.ERROR_REPORTING=0
	try:
		for a in args:
			if not executer.has_val(a):
				val_set = False
				break;
		else:
			val_set = True
	except:
		val_set = False
	
	# print "isset >> ", val_set
	executer.ERROR_REPORTING=er
	return val_set

@builtin
def empty(args, executer, local_dict):
	var = executer.get_val(args[0])
	if not var or var in (0, "", "0"):
		return False
	try:
		if len(var) == 0:
			return False
	except:
		pass
	return True

@builtin
def die(args, executer, local):
	var = executer.get_val(args[0]) if len(args) > 0 else None
	if type(var) is str:
		executer.pipe_stdout.write(var)
		var = 0
		
	raise errors.StopExecutionError(var)


@builtin
def defined(args, executer, local_dict):
	import pyphp.phpfunction as phpfunction
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
	print ("\n\n%s\n"%("Including file %s"%path))
	if once and path in executer.globals[lf_key]:
		# print " -once-> file is already included"
		pass
	else:
		import os.path
		if os.path.exists(path):
			# print " --> including file %r"%path
			import pyphp.compiler as compiler
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

def var_dump_impl(executer, x, depth=0):
	import pyphp.phparray as phparray
	dstr = "  "*depth
	t = type(x)
	if x is None:        
		executer.pipe_stdout.write("%sNULL\n"%dstr)
	elif x is True:
		executer.pipe_stdout.write("%sbool(true)\n"%dstr)
	elif x is False:
		executer.pipe_stdout.write("%sbool(false)\n"%dstr)
	elif t in (int, long):
		executer.pipe_stdout.write("%sint(%d)\n"%(dstr, x))
	elif t == str:
		executer.pipe_stdout.write("%sstring(%d) %r\n"%(dstr, len(x), x))
	elif isinstance(x, phparray.PHPArray):
		executer.pipe_stdout.write("%sarray(%d) {\n"%(dstr, len(x)))
		for y in x:
			executer.pipe_stdout.write("%s  [%r]=>\n"%(dstr, y))
			var_dump_impl(executer, x[y], depth + 1)
		executer.pipe_stdout.write("%s}\n"%dstr)
		
		
@builtin
def var_dump(args, executer, local):
	args = [executer.get_val(a) for a in args]
	for arg in args:
		var_dump_impl(executer, arg)

@builtin
def ini_set(args, executer, local):
	pass

@builtin
def error_reporting(args, executer, local):
	if len(args) > 0:
		executer.ERROR_REPORTING = executer.get_val(args[0])
	return executer.ERROR_REPORTING
