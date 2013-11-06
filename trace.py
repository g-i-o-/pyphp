trace_stack=[]
tcid = 0
trace_temps = {
	'basic' : [
		"%(indent)s%(name)s { [%(depth)d]",
		"%(indent)s} [%(depth)d] // %(name)r"
	],
	'args' : [
		"%(indent)s%(name)s (%(args)r,%(kwargs)r){ [%(depth)d]",
		"%(indent)s} [%(depth)d] // %(name)r"
	],
	'tids'  : {
		"%(indent)s%(name)s (%(args)r,%(kwargs)r){ [%(depth)d] : TPID%(parent_tcid)s -> TCID%(tcid)s",
		"%(indent)s} [%(depth)d] // %(name)r : TPID%(parent_tcid)s -> TCID%(tcid)s"
	}
}
def trace(fn, show_tids = False):
	global 	trace_temps
	pre_tt, post_tt  = trace_temps['tids' if show_tids else 'basic']
	
	def tfn(*a,**b):
		global trace_stack, tcid
		cur_tcid = tcid
		tcid += 1
		trace_stack.append(tcid)
		trace_depth = len(trace_stack)
		tpid = trace_stack[-2] if trace_depth >= 2 else None
		fn_name = fn.__name__
		pdata = {
			'indent' : "|"*trace_depth,
			'name'   : fn_name,
			'args'   : a,
			'kwargs' : b,
			'depth'  : trace_depth,
			'parent_tcid': tpid,
			'tcid'   : cur_tcid
		}
		print pre_tt % pdata
		rv = fn(*a,**b)
		print post_tt % pdata
		trace_stack.pop()
		return rv
	return tfn


def trace_obj_calls(obj, filter_fn=None, show_tids=False):
	if type(filter_fn) in(list, tuple):
		flist = filter_fn
		def ffn(x):
			return x in flist
		if flist[0] == '!':
			flist.pop(0)
			filter_fn = (lambda x: not ffn(x))
		else:
			filter_fn = ffn
	elif not filter_fn:
		filter_fn = lambda x:True
	
	for x in dir(obj):
		y = getattr(obj, x)
		if x[0] != '_' and callable(y) and filter_fn(x):
			setattr(obj, x, trace(y, show_tids))
