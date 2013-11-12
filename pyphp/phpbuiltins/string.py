from builtin import builtin
import phparray


@builtin
def str_replace(args, executer, local):
    search, replace, subject = [executer.get_val(x) for x in args[:3]]
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
        splits = subject.split(s)
        rep_count += len(splits)-1
        subject = repl.join(splits)
    if len(args) >= 4:
        executer.set_val(args[3], rep_count)
    return subject

    