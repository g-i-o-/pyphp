import re

# Verbosity levels for this module
VERBOSITY_NONE = 0
VERBOSITY_LINENUMS = 1
VERBOSITY_UNPARSEABLE_CHARS = 0
# current verbosity level
VERBOSE = VERBOSITY_NONE

# Regular expressions for the parsed tokens
RE_line_comment  = re.compile(r'(#|//)[^\n]*($|\n)')
RE_cpp_comment   = re.compile(r'/\*([^*]|\*+[^/])*\*/')
RE_whitespace    = re.compile(r'[\s\n]*')
RE_until_php_tag = re.compile(r'(([^<]|<[^?]|<\?[^p]|<\?p[^h]|<\?ph[^p])*)<\?php')
RE_php_end_tag   = re.compile(r'\?>')
RE_float         = re.compile(r'(\d*\.\d+|\d+\.)([eE][+-]?\d+)?')
RE_hexnumber     = re.compile(r'0x[a-fA-F\d]+')
RE_number        = re.compile(r'\d+')
# RE_identifier    = re.compile(r'\w[\w\d_]+')
RE_identifier    = re.compile(r'[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*')
# RE_variable      = re.compile(r'\$\w[\w\d_]+')
RE_variable      = re.compile(r'\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*')
RE_sq_string     = re.compile(r"'(([^']|\\')*)'")
RE_dq_string     = re.compile(r'"(([^"]|\\"|{\s*\$\w[\w\d_]+\["(([^"]|\\")*)"\]\s*})*)"')
RE_misc          = re.compile(r'([,();[\]{}])')
#RE_op_1  = re.compile('\|\||\|=|\||^=|\?|>>=|>>|>=|>|=>|===|==|=|<>|<=|<<=|<<|<|::|:|/=|/|.=|.|-=|-|\+=|\+|\*=|\*|&=|&|&&|%=|%|!==|!=|!')
RE_op_1  = re.compile('!==|===|instanceof|&&|\|\|')
RE_op_2  = re.compile('\.=|!=|==|<=|>=|->|=>|&|\||\^')
RE_op_3  = re.compile('!|=|<|>|~|^|::|:|\?|--|\.|\+\+|-|\+|\*|/')

STR_ESCAPE = {
	'n' : '\x0a' , 'r' : '\x0d' , 't' : '\x09' , 'v' : '\x0b' ,
	'e' : '\x1b' , 'f' : '\x0c' , '\\': '\\'   , '$' : '$'    , '"' : '"'
}

RE_start_whitespace = re.compile(r'[\s\n]')
RE_start_comment    = re.compile(r'#|\/(\/|\*)')
RE_start_variable   = re.compile(r'\$[a-zA-Z_\x7f-\xff]')
RE_start_identifier = re.compile(r'[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*')
RE_start_number     = re.compile(r'\d|\.\d')
RE_start_php_end    = re.compile(r'\?>')
RE_start_sq_string  = re.compile(r"'")
RE_start_dq_string  = re.compile(r'"')
RE_start_op         = re.compile(r'!==|===|instanceof|&&|-|\*|/|\+\+|--|\+|\|\||\.=|\.|!=|==|<=|>=|->|=>|&|\||\^|!|=|<|>|~|^|::|:|\?')
RE_start_misc       = RE_misc

RE_arrow_op = re.compile(r'->')

# Tokenized operators
TOKEN_OR_OP      = ('or', '||')
TOKEN_XOR_OP     = ('xor',)
TOKEN_AND_OP     = ('and', '&&')
TOKEN_ASSIGNMENT_OP = ('=', '+=', '-=', '*=', '/=', '.=', '%=', '&=', '|=', '^=', '<<=', '>>=', '.=')
TOKEN_BIT1_OP    = ('|', '&')
TOKEN_COMP_OP    = ('==', '!=', '===', '!==', '<', '<=', '>', '>=', 'instanceof')
TOKEN_ADD_OP     = ('+', '-' , '.')
TOKEN_TERM_OP    = ('*', '/' , '%')
TOKEN_UNARY_OP   = ('!', '~' , '++', '--', '+', '-', '@')

# Token Names
TOKEN_SET_OP        = ['!==', '===', '!=', '==', '<=', '>=', '->', '=>', '!', '=', '<', '>', '~', '^', '::', ':', '?', 'instanceof']
TOKEN_SET_MISC      = ['[', ',', '.', '(', ')', ';', '[', ']', '{', '}']
TOKEN_STRING        = "STRING"
TOKEN_INTERPOLATED_STRING = "INTSTRING"
TOKEN_NUMBER        = "NUMBER"
TOKEN_VARIABLE      = "VARIABLE"
TOKEN_IDENTIFIER    = "IDENTIFIER"
TOKEN_WS            = "WS"
TOKEN_COMMENT       = "COMMENT"
TOKEN_DIRECT_OUTPUT = "DIRECT_OUTPUT"
TOKEN_EOF           = "EOF"

class ParseError(StandardError):
	def __init__(self, message="", parser=None):
		msg=message
		if parser:
			code, i, filename = parser.code, parser.i, parser.filename
			codelen = len(code)
			line_starts = [(pos, x) for pos, x in enumerate(code) if x == '\n' and pos < i]
			line    = len(line_starts) + 1
			linestart_idx = 0 if line == 0 else line_starts[-1][0]+1
			lineend_idx   = i
			while code[lineend_idx] != '\n' and lineend_idx < codelen:
				lineend_idx += 1
			errline   = code[linestart_idx:lineend_idx]
			arrowline = " "*(i - linestart_idx + 3*len([x for x in errline if x == '\t'])) + '^'
			errline   = ''.join(["    " if x == '\t' else x for x in errline])
			msg = "File \"%s\", line %s : %s\n%s\n%s"%(filename, line, message, errline, arrowline)
		super(StandardError, self).__init__(msg)

class TokenList(list):
	pass
class Token():
	def __init__(self, parts, filename, linenum):
		self.parts = parts
		self.filename = filename
		self.line_num = linenum
	def __len__(self):
		return len(self.parts)
	def __getitem__(self, idx):
		return self.parts[idx]
	def __repr__(self):
		return "Token%r%s"%(self.parts, "[file:%r,line:%s]"%(self.filename, self.line_num) if VERBOSE >= VERBOSITY_LINENUMS else '')

class Parser:
	def __init__(self, code, filename='<inline code>'):
		self.code = code
		self.i=0
		self.filename=filename
		self.line_num=1;
		self.in_code = False
		self.tokens = TokenList()
		self.tokens
	
	def parse(self):
		codelen = len(self.code)
		php_code = self.code
		while self.i < codelen:
			if self.in_code:
				self.parse_all()
				self.parse_phpendtag()
				if self.i < len(self.code):
					c=php_code[self.i]
					print ParseError("", self)
			else:
				self.read_outcode()
			self.i += 1
		return self.tokens
	
	def parse_phpendtag(self):
		if RE_php_end_tag.match(self.code, self.i):
			self.i += 2
			self.in_code = False
	
	def parse_all(self):
		loop=True
		codelen = len(self.code)
		code = self.code
		while loop and self.i < codelen:
			old_i = self.i
			c  = code[self.i]
			nc = code[self.i + 1] if self.i + 1 < codelen else None
			if RE_start_whitespace.match(code, self.i) is not None:
				self.parse_whitespace()
			elif RE_start_comment.match(code, self.i):
				self.parse_comments()
			elif RE_start_php_end.match(code, self.i):
				self.parse_phpendtag()
				self.read_outcode()
			elif RE_start_sq_string.match(code, self.i):
				self.parse_string()
			elif RE_start_dq_string.match(code, self.i):
				self.parse_interp_string()
			elif RE_start_variable.match(code, self.i):
				self.parse_variable()
			elif RE_start_number.match(code, self.i):
				self.parse_number()
			elif RE_start_op.match(code, self.i):
				self.parse_op()
			elif RE_start_identifier.match(code, self.i):
				self.parse_identifier()
			elif RE_start_misc.match(code, self.i):
				self.parse_misc()
			else:
				raise ParseError("Cannot parse.", self)
			loop = old_i != self.i
			
	def parse_op(self):
		op_m = RE_op_1.match(self.code, self.i)
		if not op_m:
			op_m = RE_op_2.match(self.code, self.i)
		if not op_m:
			op_m = RE_op_3.match(self.code, self.i)
		if not op_m:
			return
		m_text = op_m.group(0)
		if len(m_text) > 0:
			self.tokens.append(Token([m_text], self.filename, self.line_num))
			self.i += len(m_text)
			
	def parse_misc(self, tokens = None):
		m_m = RE_misc.match(self.code, self.i)
		if not m_m:
			return
		m_text = m_m.group(0)
		if len(m_text) > 0:
			if tokens  is None:
				tokens = self.tokens
			tokens.append(Token([m_text], self.filename, self.line_num))
			self.i += len(m_text)
			
	def parse_string(self):
		s_m = RE_sq_string.match(self.code, self.i)
		if not s_m:
			return
		s_text = s_m.group(1)
		self.tokens.append(Token([TOKEN_STRING, s_text], self.filename, self.line_num))
		self.i += len(s_m.group(0))
			
	def parse_interp_string(self, tokens = None):
		code = self.code
		if code[self.i] != '"':
			raise ParseError('Interpolated string must start with a "')
		self.i+=1
		start=self.i
		txt=[]
		text_seq=[]
		interp=[]
		clen = len(self.code)
		interp_count=0
		
		while self.i < clen:
			c = self.code[self.i]
			if c=='"':
				break
			elif c == "\\":
				c = self.code[self.i + 1]
				if c in STR_ESCAPE:
					txt.append(STR_ESCAPE[c])
					self.i += 2
				else:
					m = RE_octal_chr.match(self.code, self.i)
					base=8
					if not m:
						m = RE_hex_chr.match(self.code, self.i)
						base=16
					if m:
						num = m.group(1)
						txt.append(chr( int(num, base) ))
						self.i += len(m.group(0))
					else:
						txt.append("\\" + c)
						self.i += 2
			elif c == '$':
				if not RE_start_variable.match(code, self.i):
					txt.append(code[self.i])
					self.i+=1
				else:
					interp_tokens = self.parse_interpolation(TokenList())
					if interp_tokens is None:
						txt.append(code[self.i])
						self.i+=1
					else:
						ep = self.i
						text_seq.append(''.join(txt))
						text_seq.append(interp_tokens)
						interp_count += 1
						txt = []
			elif c == '{':
				sp = self.i
				self.i += 1# + len(self.read_whitespace())
				c = code[self.i]
				if c == '$':
					interp_tokens = self.parse_interpolation(TokenList())
					if interp_tokens is not None:
						self.parse_whitespace(interp_tokens)
						if code[self.i] != '}': # interpolation must end in a '}'
							interp_tokens = None
					if interp_tokens is None:
						txt.append(code[sp: self.i])
					else:
						ep = self.i
						text_seq.append(''.join(txt))
						text_seq.append(interp_tokens)
						interp_count += 1
						txt = []
				else:
					txt.append(code[sp: self.i])
			else:
				txt.append(c)
				self.i += 1
		if len(txt) > 0:
			text_seq.append(''.join(txt))
		if tokens is None:
			tokens = self.tokens
		if interp_count == 0:
			tokens.append(Token([TOKEN_STRING, ''.join(text_seq)], self.filename, self.line_num))
		else:
			tokens.append(Token([TOKEN_INTERPOLATED_STRING, text_seq], self.filename, self.line_num))
		self.i += 1
	
	def parse_interpolation(self, tokens, allow_identifier=False, allow_number=False):
		code = self.code
		if RE_start_variable.match(code, self.i):
			self.parse_variable(tokens)
		elif allow_identifier and RE_start_identifier.match(code, self.i):
			self.parse_identifier(tokens)
		elif allow_number and RE_start_number.match(code, self.i):
			self.parse_number(tokens)
		else:
			return None # invalid token, but without any errors, since this function is internal
		if RE_arrow_op.match(code, self.i):
			tokens.append(Token(['->'], self.filename, self.line_num))
			self.i += 2
			self.parse_whitespace(tokens)
			return self.parse_interpolation(tokens, True, False)
		elif code[self.i] == '[':
			self.i += 1
			self.parse_whitespace(tokens)
			interp = self.parse_interpolation(tokens, True, True)
			self.parse_whitespace(tokens)
			if code[self.i] == ']':
				return interp
			else:
				return None
		else:
			return tokens

	def parse_number(self, tokens=None):
		var_m = RE_float.match(self.code, self.i)
		num_t = 1
		if not var_m:
			var_m = RE_hexnumber.match(self.code, self.i)
			num_t = 2
		if not var_m:
			var_m = RE_number.match(self.code, self.i)
			num_t = 3
		if not var_m:
			return
		var_text = var_m.group(0)
		if len(var_text) > 0:
			num = float(var_text) if num_t == 1 else int(var_text, 16 if num_t == 2 else (8 if var_text[0] == '0' else 10))
			if tokens is None:
				tokens = self.tokens
			tokens.append(Token([TOKEN_NUMBER, num], self.filename, self.line_num))
			self.i += len(var_text)

	def parse_variable(self, tokens=None):
		var_text = self.read_variable()
		if not var_text:
			return
		if len(var_text) > 0:
			if tokens is None:
				tokens = self.tokens
			tokens.append(Token([TOKEN_VARIABLE, var_text], self.filename, self.line_num))
			self.i += len(var_text)
	
	def read_variable(self):
		var_m = RE_variable.match(self.code, self.i)
		if not var_m:
			return
		else:
			return var_m.group(0)
		
	def read_whitespace(self):
		return RE_whitespace.match(self.code, self.i).group(0)
	
	def parse_identifier(self, tokens=None):
		id_m = RE_identifier.match(self.code, self.i)
		if not id_m:
			return
		id_text = id_m.group(0)
		if len(id_text) > 0:
			if tokens is None:
				tokens = self.tokens
			tokens.append(Token([TOKEN_IDENTIFIER, id_text], self.filename, self.line_num))
			self.i += len(id_text)


	def parse_whitespace(self, tokens=None):
		ws_text = self.read_whitespace()
		if tokens is None:
			tokens = self.tokens
		if len(ws_text) > 0:
			tokens.append(Token([TOKEN_WS], self.filename, self.line_num))
			self.i += len(ws_text)
			self.line_num += len([x for x in ws_text if x == '\n'])
		
	def parse_comments(self):
		c_m = RE_line_comment.match(self.code, self.i)
		if c_m is None:
			c_m = RE_cpp_comment.match(self.code, self.i)
		if c_m is not None:
			c_text = c_m.group(0)
			self.tokens.append(Token([TOKEN_COMMENT, c_text], self.filename, self.line_num))
			self.line_num += len([x for x in c_m.group(0) if x == '\n'])
			self.i += len(c_text)
		
	def read_outcode(self):
		outcode_m = RE_until_php_tag.match(self.code, self.i)
		if outcode_m :
			outcode_text = outcode_m.group(1)
			if len(outcode_text) > 0:
				self.tokens.append(Token([TOKEN_DIRECT_OUTPUT, outcode_text], self.filename, self.line_num))
			self.i += len(outcode_text) + 4
			self.line_num += len([x for x in outcode_m.group(0) if x == '\n'])
		self.in_code = True

def parse_file(php_file, state=None):
	code=None
	from os.path import abspath
	with file(abspath(php_file)) as finp:
		code = finp.read()
	P = Parser(code, php_file)
	return P.parse()

def parse_php(php_code, state=None):
	P = Parser(php_code)
	return P.parse()


TEST_CODE = """<?php
/**
 * Configures php for use in a local CLI environment.
 * NEVER (repeat !!!NEVER!!!) use this particular config file
 * for scripts requested from apache, as
 * some $_SERVER values are set here that may conflict......
 * 		att. Gio
 * @log[may 9 2013] : v 1.0
 * 		Derived from config.inc.php in /usr/local/arbimon/daemon
 */
// define the running environment as CLI
define('RUN_ENV', 'CLI');
?>
what what!!
<?php

/**
 * Defines a set of this that are normally defined by apache.
 */
// document root (root for web server)
$_SERVER['DOCUMENT_ROOT'] = '/Library/WebServer/Documents/';
// server name (should this be picked up from hostname?)
if(!isset($_SERVER['SERVER_NAME'])){
	$_SERVER['SERVER_NAME'] = 'arbimonrec.uprrp.edu';
}
// server listen port (http is 80)
if(!isset($_SERVER['SERVER_PORT'])){
	$_SERVER['SERVER_PORT'] = 80;
	$_SERVER['SERVER_PORT_2'] = 800.11;
}

// APP_ROOT is the root for the php web app
// define('APP_ROOT', $_SERVER['DOCUMENT_ROOT'] . 'sandboxes/gio');
define('APP_ROOT', $_SERVER['DOCUMENT_ROOT'] . 'app/service');


// loads the arbimon's server configuration
// require_once("/usr/local/arbimon/config/config.inc.php");

?>"""

def test(*args, **kw):
	if len(args) > 0:
		kw['code'] = args[0]
	if 'filename' in kw:
		filename = kw['filename']
		print "parsing file : %r"%filename
		from os.path import abspath
		with file(abspath(filename)) as finp:
			print finp.read()
		print "----"
		parsed_code = parse_file(filename)
	elif 'code' in kw:
		code = kw['code']
		print "parsing php code :\n%s"%code
		print "----"
		parsed_code = parse_php(code)
	print
	print "Parsed Code:\n", '\n'.join([`x` for x in parsed_code])
	

if __name__ == '__main__':
	import sys
	if len(sys.argv) >= 2:
		test(filename=sys.argv[1])
	else:
		test(code=TEST_CODE)