#! /usr/bin/python

import sys
import parser
import compiler
import executer
import scope
import phparray

NAME   ='pyphp.py'
VERSION='0.1'

USAGE = """{0}
   Php parser, compiler and interpreter, in python
   v. {1}

Usage:
  {2} [--parse | --compile | --run] script.php [script-args*]
""".format(NAME, VERSION, sys.argv[0])

if __name__ == '__main__':
	# print sys.argv
	action = 'run'
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
				elif key in ('compile', 'run', 'parse'):
					action = key
				else:
					print "Unknown option %s"%arg
			else:
				if len(phpargv) == 0:
					phpfile = arg
				phpargv.append(arg)
				
	init_scope = {
		'$argv' : phparray.PHPArray(*enumerate(phpargv)),
		'$argc' : len(phpargv)
	}
	
	if phpfile:
		if action == 'run':
			php_executer = executer.execute_file(phpfile, init_scope)
			if show_globals:
				print "[ended]\n-- globals --"
				for i in executer.globals.dict:
					print "%-14s  ->  %r"%(i, executer.globals[i])
		elif action == 'compile':
			code_tree = compiler.compile_file(phpfile)
			print "[ended compilation]\n-- code tree --"
			print code_tree.prepr()
		elif action == 'parse':
			tokens = parser.parse_file(phpfile)
			print "[ended parsing]\n-- tokens --"
			print ' '.join([repr(x) for x in tokens])
		
	else :
		print "# No file to %s!"%action
		print USAGE
		
