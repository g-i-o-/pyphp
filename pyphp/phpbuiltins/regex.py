from builtin import builtin
import constants
import pyphp.phparray as phparray
#import re

WARN_NOT_PCRE = False
USING_PCRE = False



if USING_PCRE:
    try:
        import pcre as re
        USING_PCRE = True
    except ImportError, ie: 
        USING_PCRE = False
        



if USING_PCRE:
    def parse_regex(pat):
        return pat, 0
else:
    import re
    WARNING_GIVEN = not WARN_NOT_PCRE
    def warn(executer):
        global WARNING_GIVEN
        if not WARNING_GIVEN:
            executer.report_error(constants.E_CORE_WARNING, "Python's re module is not completely compatible to PCRE.")
            WARNING_GIVEN=True
        
    def parse_regex(pat):
        delimiter = pat[0]
        i, e = 1, len(pat)
        while i < e:
            c = pat[i]
            if c == '\\' and i+1<e and pat[i+1] == delimiter:
                pat = pat[:i] + delimiter + pat[i+2:]
                e -= 1
                i += 1
            elif c == delimiter:
                i += 1
                break
            else:
                i += 1
        regex = pat[1:(i-1)]
        flags = 0
        if i < e:
            while i < e:
                c = pat[i]
                if c == 'i':
                    flags |= re.IGNORECASE
                elif c == 'm':
                    flags |= re.MULTILINE
                elif c == 's':
                    flags |= re.DOTALL
                i += 1
        return regex, flags

@builtin
def preg_replace(args, executer, local):
    global USING_PCRE
    # mixed preg_replace ( mixed $pattern , mixed $replacement , mixed $subject [, int $limit = -1 [, int &$count ]] )
    pattern, replacement, subject = [executer.get_val(x) for x in args[:3]]
    limit = 0 if len(args) < 4 else executer.get_val(args[3])
    count_ref  = None if len(args) < 5 else args[4]
    # print dict(zip('pattern,replacement,subject'.split(','), [pattern, replacement, subject]))
    # print '\n'.join(repr(x) for x in  [pattern, replacement, subject, limit, count_ref])
    # print local
    if not USING_PCRE:
        warn(executer)
        if isinstance(pattern, phparray.PHPArray):
            pattern = pattern.values()
        else:
            pattern = [str(pattern)]
        if isinstance(replacement, phparray.PHPArray):
            replacement = replacement.values()
        else:
            replacement = [replacement] * len(pattern)
        rep_len = len(replacement)
        total_subs = 0
        for i, pat in enumerate(pattern):
            if i < rep_len:
                repl = replacement[i]
            else:
                repl=''
            regex, flags = parse_regex(pat)
            subject, subs_made = re.subn(regex, repl, subject, limit, flags)
            total_subs+=subs_made
        if len(args) >= 4:
            executer.set_val(args[4], subs_made)
        return subject
    raise StandardError()
