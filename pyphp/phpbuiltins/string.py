from builtin import builtin
import phparray
import coerce

@builtin
def str_replace(args, executer, local):
    import prepr
    search, replace, subject = map(executer.get_val, args[:3])
    #print '\n='*90
    #print {'search':search,'replace':replace,'subject':subject}
    if isinstance(search, phparray.PHPArray):
        search = search.values()
    else:
        search = [search]
    if isinstance(replace, phparray.PHPArray):
        replace = replace.values()
    else:
        replace = [replace] * len(search)
    rep_len = len(replace)
    rep_count = 0
    for i, s in enumerate(search):
        if i < rep_len:
            repl = replace[i]
        else:
            repl=''
        #print '    =>', {'search':s,'replace':repl,'subject':subject}
        splits = subject.split(s)
        rep_count += len(splits)-1
        subject = repl.join(splits)
    #print '    ::', repr(subject)
    if len(args) >= 4:
        executer.set_val(args[3], rep_count)
    #print '\n='*90
    return subject

@builtin
def strtolower(args, executer, local):
    val = executer.get_val(args[0])
    return coerce.to_string(val).lower()
