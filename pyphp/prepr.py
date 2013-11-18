def prepr(x, depth=0, dchr=' '):
	xt = type(x)
	if hasattr(x, 'prepr'):
		return x.prepr(depth, dchr)
	elif xt in (list, tuple):
		dstr = dchr*depth
		return '%s%s'%(dstr, ('%s\n'%dstr).join([prepr(ix, depth+1, dchr) for ix in x]))
	else:
		return repr(x)