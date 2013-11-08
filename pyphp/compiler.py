import parser
import weakref

# Verbosity levels for this module
VERBOSITY_NONE = 0
VERBOSITY_SHOW_COMPILED_STATEMENTS = 1
VERBOSITY_SHOW_SKIPPED_WS          = 2
VERBOSITY_SHOW_READ_TOKENS         = 3
VERBOSITY_TRACE_GRAMMAR            = 4
# current verbosity level
VERBOSE = 0

# currently understood PHP keywords
KEYWORD_DEFINE = 'define';
KEYWORD_IF     = 'if';
KEYWORD_ELSE   = 'else';
KEYWORD_CLASS  = 'class';
KEYWORD_VAR    = 'var';
KEYWORD_NEW    = 'new';
KEYWORD_FOR    = 'for';
KEYWORD_ARRAY  = 'array';
KEYWORD_FOREACH= 'foreach';
KEYWORD_RETURN = 'return';
KEYWORD_FUNCTION  = 'function';
KEYWORD_PUBLIC    = 'public';
KEYWORD_PROTECTED = 'protected';
KEYWORD_PRIVATE   = 'private';
KEYWORD_EXTENDS   = 'extends';
KEYWORD_INSTANCEOF= 'instanceof';
KEYWORD_CONST     = 'const';
KEYWORD_ECHO      = 'echo';

VARDEF_DECORATORS = ('var', 'public', 'private', 'protected', 'static');

# operators
OPERATORS_MULT       = ('*', '/', '%')
OPERATORS_ADD        = ('+', '-', '.')
OPERATORS_BITSHIFT   = ('<<', '>>')
OPERATORS_ORDER_COMP = ('<', '<=', '>', '>=')
OPERATORS_EQ_COMP    = ('==', '!=', '===', '!==', '<>')
OPERATORS_ASSIGNMENT = ('=', '+=', '-=', '*=', '/=', '.=', '%=', '&=', '|=', '^=', '<<=', '>>=') #, '=>')


# associativity constanpytt
RIGHT_ASSOCIATIVE = True
LEFT_ASSOCIATIVE  = False

class CompileError(StandardError):
	"An Error ocurring during the compilation phase"
	pass

class TreeNode(object):
	"A node in the Abstract Syntax Tree generated from the code"
	def __init__(self, node_name, children, filename=None, line_num=0):
		"Create a TreeNode with the given name and each children appended to it"
		self.name = node_name
		self.filename=filename
		self.line_num=line_num
		self.parent = None
		self.children = []
		for child in children:
			self.addChild(child)
	def addChild(self, child):
		"Appends a child to this TreeNode.If the child is itself a TreeNode, then the child's parent is set to this."
		self.children.append(child)
		if isinstance(child, TreeNode):
			child.parent = weakref.ref(self)
	def getParent(self):
		"Returns this TreeNode's parent, if any has been set."
		if self.parent:
			return self.parent()
		else:
			return None
	def __repr__(self):
		"Returns a string representation of this TreeNode"
		return "TreeNode<%s>%r"%(self.name, self.children)
	def prepr(self, depth=0):
		dstr = "  "*depth
		return "%sTreeNode<%s, file:%r, line:%s>[\n%s\n%s]"%(
			dstr, self.name, self.filename, self.line_num, "\n".join([x.prepr(depth+1) if hasattr(x,'prepr') else ("  "*(depth+1) + str(x)) for x in self.children]), dstr
		)

class Compiler(object):
	def __init__(self, tokens=None):
		self.i = 0
		self.tokens = tokens
		self.tree   = None
		self.indent = 0
		
		if VERBOSE >= VERBOSITY_TRACE_GRAMMAR:
			import trace
			trace.trace_obj_calls(self, ['!', 'cur_filename_line', 'cur_token', 'compile', 'compile_php_file', 'skip_comments_and_ws', 'skip_to_next'])
		
		#for i in dir(self):
		#	at = getattr(self, i)
		#	if i[0] != '_' and callable(at) and i not in []:
		#		setattr(self, i, trace(at))
		
	# Utility member functions
	def cur_filename_line(self):
		tok = self.tokens[self.i] if self.i < len(self.tokens) else (parser.TOKEN_EOF, )
		return tok.filename, tok.line_num
	def cur_token(self):
		"Returns the current token."
		tok = self.tokens[self.i] if self.i < len(self.tokens) else (parser.TOKEN_EOF, )
		if VERBOSE >= VERBOSITY_SHOW_READ_TOKENS:
			print "%s%s"%("  "*self.indent, tok)
		return tok
	def skip_to_next(self):
		"Advances to the next non-ws, non-comment token."
		self.i += 1
		self.skip_comments_and_ws()
	def skip_comments_and_ws(self):
		"Consumes tokens untils a non-ws, non-comment token is found."
		tok = self.cur_token()
		while self.i < len(self.tokens) and tok[0] in (parser.TOKEN_COMMENT, parser.TOKEN_WS):
			if VERBOSE >= VERBOSITY_SHOW_SKIPPED_WS:
				print "Skipping ws : %r"%tok
			self.i += 1
			tok = self.cur_token()
	def expect_token(self, *parts):
		"checks the current token against the given parts arguments, and throws an error if they are not equal."
		token = self.cur_token()
		for i, p in enumerate(parts):
			if token[i] != p:
				raise CompileError("File:%s, line:%s, Expected %s instead of %s"%(token.filename, token.line_num, ' '.join([str(x) for x in parts]), ' '.join([str(x) for x in token])))
	def expect_sequence(self, *expected_tokens):
		sequence=[]
		for exp_tok in expected_tokens:
			if callable(exp_tok):
				sequence.append(exp_tok())
			else:
				sequence.append(self.cur_token())
				self.expect_token(*exp_tok)
				self.skip_to_next()
		return sequence
	def compile_delimited_var_list(self, list_name, element_compiler, delimiter_set, right_associative=True):
		"Compiles a list of variables following the rule list_name -> element [delimiter element]*"
		def var_list_gen():
			yield (None, element_compiler())
			while self.cur_token()[0] in delimiter_set:
				tok = self.cur_token()
				self.skip_to_next();
				yield (tok, element_compiler())
		exp_list=[]
		if right_associative:
			is_first=True
			for token, element in var_list_gen():
				if is_first:
					exp_list.append(element)
					is_first = False
				else:
					exp_list.append(TreeNode(token[0], [element], token.filename, token.line_num))
		else:
			last_element=None
			for token, element in var_list_gen():
				if last_element:
					exp_list.append(TreeNode(token[0], [last_element], token.filename, token.line_num))
				last_element = element
			exp_list.append(last_element)
		return TreeNode(list_name, exp_list, exp_list[0].filename, exp_list[0].line_num) if len(exp_list) > 1 else exp_list[0]
	# Grammar Compilation functions
	def compile(self, tokens=None): # => php_file
		"Starting point, resets this compiler's state and starts the compilation process"
		self.i=0
		self.indent=0
		self.tree=self.compile_php_file()
		return self.tree
	def compile_php_file(self): # php_file => stmt+
		fn, ln = self.cur_filename_line()
		stmts=[]
		while self.i < len(self.tokens):
			stmts.append(self.compile_stmt())
		return TreeNode("php_file", stmts, fn, ln)
	def compile_stmt(self): # stmt => define_stmt | direct_output | expression_stmt | if_stmt | stmt_block | classdef_stmt | return_stmt | foreach_stmt
		self.skip_comments_and_ws()
		token = self.cur_token()
		stmt = None
		if VERBOSE >= VERBOSITY_SHOW_READ_TOKENS:
			print "compiling stmt, %s"%token 
		if token[0] == parser.TOKEN_IDENTIFIER:
			ident_lc_name = token[1].lower();
			if ident_lc_name == KEYWORD_DEFINE:
				stmt = self.compile_define_stmt()
			elif ident_lc_name == KEYWORD_IF:
				stmt = self.compile_if_stmt()
			elif ident_lc_name == KEYWORD_FOR:
				stmt = self.compile_for_stmt()
			elif ident_lc_name == KEYWORD_FUNCTION:
				stmt = self.compile_funcdef_stmt()
			elif ident_lc_name == KEYWORD_FOREACH:
				stmt = self.compile_foreach_stmt()
			elif ident_lc_name == KEYWORD_RETURN:
				stmt = self.compile_return_stmt()
			elif ident_lc_name == KEYWORD_CLASS:
				stmt = self.compile_classdef_stmt()
			elif ident_lc_name == KEYWORD_ECHO:
				stmt = self.compile_echo_stmt()
		elif token[0] == parser.TOKEN_DIRECT_OUTPUT:
			out_str = token[1]
			if len(out_str) > 0 and out_str[0] == '\n':
				out_str = out_str[1:]
			if len(out_str) > 0 and out_str[-1] == '\n':
				out_str = out_str[:-1]
			stmt = TreeNode("direct_output", [out_str], token.filename, token.line_num)
			self.skip_to_next()
		elif token[0] == '{':
			stmt = self.compile_stmt_block()
		
		if stmt is None:
			stmt = self.compile_expression_stmt()
			
		if stmt is None:
			raise CompileError("File:%s, line:%s, Expected stmt instead of %s"%(token.filename, token.line_num, ' '.join([str(x) for x in token])))
		
		if VERBOSE >= VERBOSITY_SHOW_COMPILED_STATEMENTS:
			print "@@ %s"%stmt
		return stmt
	def compile_echo_stmt(self):         # echo_stmt          => ECHO expression_list
		fn, ln = self.cur_filename_line()
		self.expect_token(parser.TOKEN_IDENTIFIER, KEYWORD_ECHO)
		self.skip_to_next()
		args = [];
		if self.cur_token()[0] != ';':
			args = self.compile_expression_list().children
		self.expect_token(';')
		self.skip_to_next()
		return TreeNode('echo', args, fn, ln)
		
	def compile_stmt_block(self):        #  stmt_block        => '{' [stmt]* '}'
		tok = self.tokens[self.i]
		fn = tok.filename
		ln = tok.line_num
		self.expect_token('{')
		self.skip_to_next()
		tok = self.cur_token()
		stmts = []
		while tok[0] != '}':
			stmts.append(self.compile_stmt())
			tok = self.cur_token()
		self.skip_to_next()
		return TreeNode('stmt_block', stmts, fn, ln)
	def compile_define_stmt(self):       #  define_stmt       => 'define' argument_list ';'
		self.expect_token(parser.TOKEN_IDENTIFIER, KEYWORD_DEFINE)
		self.skip_to_next()
		argument_list = self.compile_argument_list()
		if len(argument_list.children) != 2:
			raise CompileError("define stmt accepts only 2 arguments.");
		self.expect_token(';')
		self.skip_to_next()
		return TreeNode(KEYWORD_DEFINE, argument_list.children, argument_list.filename, argument_list.line_num)
	def compile_return_stmt(self):       #  return_stmt       => RETURN expression ';'
		fn, ln = self.cur_filename_line()
		seq = self.expect_sequence(
			(parser.TOKEN_IDENTIFIER, KEYWORD_RETURN),
			self.compile_expression,
			(';', )
		)
		return TreeNode('return_stmt', [seq[1]], fn, ln)
	def compile_for_stmt    (self):              #  for_stmt        => FOR '(' expression_list ';' expression_list ';' expression_list ')' stmt_block
		fn, ln = self.cur_filename_line()
		seq = self.expect_sequence(
			(parser.TOKEN_IDENTIFIER, KEYWORD_FOR),
			('(', ),
			self.compile_expression_list,
			(';', ),
			self.compile_expression_list,
			(';', ),
			self.compile_expression_list,
			(')', ),
			self.compile_stmt_block
		)
		return TreeNode('for_stmt', [seq[2], seq[4], seq[6], seq[8]], fn, ln)
	def compile_foreach_stmt(self):              #  foreach_stmt    => FOREACH '(' VARIABLE AS VARIABLE [ '=>' VARIABLE ] ')' stmt_block
		fn, ln = self.cur_filename_line()
		seq = self.expect_sequence(
			(parser.TOKEN_IDENTIFIER, KEYWORD_FOREACH),
			('(', ),
			self.compile_followed_primitive,
			(parser.TOKEN_IDENTIFIER, 'as'),
			self.compile_followed_primitive
		)
		seq2 = None
		if self.cur_token()[0] == '=>':
			seq2 = self.expect_sequence(
				('=>', ),
				self.compile_followed_primitive
			)
		seq3 = self.expect_sequence(
			(')', ),
			self.compile_stmt_block
		)
		return TreeNode("foreach_stmt", [seq[2], seq[4], seq2[1] if seq2 is not None else None, seq3[1]], fn, ln)
	def compile_argument_list(self):          #  argument_list          => '(' [argument [ ',' argument ]*] ')'
		fn, ln = self.cur_filename_line()
		args_list=[]
		tok = self.tokens[self.i]
		self.expect_token('(')
		self.skip_to_next()
		while self.cur_token()[0] != ')' :
			args_list.append(self.compile_argument())
			if self.cur_token()[0] == ')':
				break
			else:
				self.expect_token(',')
				self.skip_to_next()
		self.skip_to_next()
		return TreeNode("argument_list", args_list, fn, ln)
	
	def compile_argument(self):               #  argument               => expression
		return self.compile_expression()
	
	def compile_expression_stmt(self):   #  expression_stmt   => expression ';'
		expr = self.compile_expression();
		self.expect_token(';')
		self.skip_to_next()
		return expr;
	
	def compile_expression_list(self):   # expression_list    => expression [ ',' expression ]*
		fn, ln = self.cur_filename_line()
		l = [self.compile_expression()]
		while self.cur_token()[0] == ',':
			self.skip_to_next()
			l.append(self.compile_expression())
		return TreeNode('expression_list', l, fn, ln)
	def compile_expression            (self):         #  expression                  =>    or_expression
		return self.compile_or_expression()
	def compile_or_expression         (self):         #  or_expression               =>    xor_expression [OR xor_expression]*
		return self.compile_delimited_var_list("or_expression", self.compile_xor_expression, ['or'])
	def compile_xor_expression        (self):         #  xor_expression              =>    and_expression [XOR and_expression]*
		return self.compile_delimited_var_list("xor_expression", self.compile_and_expression, ['xor'])
	def compile_and_expression        (self):         #  and_expression              =>    assignment_expression [AND assignment_expression]*
		return self.compile_delimited_var_list("and_expression", self.compile_assignment_expression, ['and'])
	def compile_assignment_expression (self):         #  assignment_expression       =>    conditional_expression [assignment_op conditional_expression]
		return self.compile_delimited_var_list("assignment_expression", self.compile_conditional_expression, OPERATORS_ASSIGNMENT, LEFT_ASSOCIATIVE)
	def compile_conditional_expression(self):         #  conditional_expression      =>    sym_or_expression ['?' sym_or_expression ':' sym_or_expression ]
		fn, ln = self.cur_filename_line()
		exp1 = self.compile_sym_or_expression()
		if self.cur_token()[0] == '?':
			seq = self.expect_sequence(
				['?'],
				self.compile_sym_or_expression,
				[':'],
				self.compile_sym_or_expression
			)
			return TreeNode('conditional_expression', [exp1, seq[1], seq[3]], fn, ln)
		return exp1
	def compile_sym_or_expression     (self):         #  sym_or_expression           =>    sym_and_expression ['||' sym_and_expression]*
		return self.compile_delimited_var_list("sym_or_expression", self.compile_sym_and_expression, ['||'])
	def compile_sym_and_expression    (self):         #  sym_and_expression          =>    bit_or_expression  ['&&' bit_or_expression ]*
		return self.compile_delimited_var_list("sym_and_expression", self.compile_bit_or_expression, ['&&'])
	def compile_bit_or_expression     (self):         #  bit_or_expression           =>    bit_xor_expression ['|' bit_xor_expression]*
		return self.compile_delimited_var_list("bit_or_expression", self.compile_bit_xor_expression, ['|'])
	def compile_bit_xor_expression     (self):         #  bit_or_expression           =>    bit_and_expression ['|' bit_and_expression]*
		return self.compile_delimited_var_list("bit_xor_expression", self.compile_bit_and_expression, ['^'])
	def compile_bit_and_expression    (self):         #  bit_and_expression          =>    eq_comp_expression ['&' eq_comp_expression]*
		return self.compile_delimited_var_list("bit_and_expression", self.compile_eq_comp_expression, ['&'])
	def compile_eq_comp_expression    (self):         #  eq_comp_expression          =>    order_comp_expression [eq_comp_op order_comp_expression]*
		return self.compile_delimited_var_list("eq_comp_expression", self.compile_order_comp_expression, OPERATORS_EQ_COMP)
	def compile_order_comp_expression (self):         #  order_comp_expression       =>    bitshift_expression   [order_comp_op bitshift_expression]*
		return self.compile_delimited_var_list("order_comp_expression", self.compile_bitshift_expression, OPERATORS_ORDER_COMP)
	def compile_bitshift_expression   (self):         #  bitshift_expression         =>    add_expression [bitshift_op add_expression]*
		return self.compile_delimited_var_list("bitshift_expression", self.compile_add_expression, OPERATORS_BITSHIFT)
	def compile_add_expression        (self):         #  add_expression              =>    term [add_op term]*
		return self.compile_delimited_var_list("add_expression", self.compile_term, OPERATORS_ADD)
	def compile_term                  (self):         #  term                        =>    negated_typecheck [mult_op negated_typecheck]*
		return self.compile_delimited_var_list("term_expression", self.compile_negated_typecheck, OPERATORS_MULT)
	def compile_negated_typecheck     (self):         #  negated_typecheck           =>    ['!'] typecheck
		fn, ln = self.cur_filename_line()
		negated = False
		if self.cur_token()[0] == '!':
			negated = True
			self.skip_to_next()
		tchk = self.compile_typecheck()
		if negated:
			return TreeNode('negated', [tchk])
		else:
			return tchk
	def compile_typecheck             (self):         #  typecheck                   =>    factor ['instanceof' typedef]
		fn, ln = self.cur_filename_line()
		factor = self.compile_factor()
		tok = self.cur_token()
		if tok[0] == KEYWORD_INSTANCEOF:
			self.skip_to_next()
			td = self.compile_typedef()
			return TreeNode('typecheck', [factor, td], fn, ln)
		return factor

	def compile_factor(self):                 #  factor                 => [unary_operator]* followed_primitive
		args=[]
		unary_ops = []
		while self.cur_token()[0] in parser.TOKEN_UNARY_OP:
			unary_ops.append(self.cur_token())
			self.skip_to_next()
		if len(unary_ops) > 0:
			args.append(TreeNode("unary_op", [x[0] for x in unary_ops], unary_ops[0].filename, unary_ops[0].line_num))
		args.append(self.compile_followed_primitive())
		return TreeNode("factor", args, args[0].filename, args[0].line_num) if len(args) > 1 else args[0]
	
	def compile_followed_primitive(self):     # followed_primitive      => primitive [primitive_follower]*
		args=[]
		args.append(self.compile_primitive())
		while True:
			try:
				follower = self.compile_primitive_follower()
				args.append(follower)
			except CompileError, ce:
				break
		return TreeNode("followed_primitive", args, args[0].filename, args[0].line_num) if len(args) > 1 else args[0]

	
	def compile_primitive(self):              #  primitive              => string | number | identifier | variable | '(' expression ')' | NEW typedef argument_list | array_literal
		tok=self.cur_token()
		if tok[0] == parser.TOKEN_IDENTIFIER and tok[1] == KEYWORD_NEW:
			seq = self.expect_sequence(
				(parser.TOKEN_IDENTIFIER, KEYWORD_NEW),
				self.compile_typedef,
				self.compile_argument_list
			)
			return TreeNode("primitive", [tok, seq[1], seq[2]], tok.filename, tok.line_num)
		elif tok[0] == parser.TOKEN_IDENTIFIER and tok[1] == KEYWORD_ARRAY:
			return TreeNode("primitive", [self.compile_array_literal()], tok.filename, tok.line_num)
		elif tok[0] in (parser.TOKEN_STRING, parser.TOKEN_NUMBER, parser.TOKEN_IDENTIFIER, parser.TOKEN_VARIABLE):
			self.skip_to_next()
			return TreeNode("primitive", [tok], tok.filename, tok.line_num)
		elif tok[0] == parser.TOKEN_INTERPOLATED_STRING:
			interpolations = tok[1]
			for i, interp in enumerate(interpolations):
				if isinstance(interp, parser.TokenList):
					if VERBOSE > VERBOSITY_NONE:
						print "=================================================="
					C = Compiler(interp)
					interpolations[i] = C.compile_factor()
					if VERBOSE > VERBOSITY_NONE:
						print "=================================================="
			self.skip_to_next()
			return TreeNode("primitive", [tok], tok.filename, tok.line_num)
		else:
			self.expect_token('(')
			self.skip_to_next()
			expr = self.compile_expression()
			self.expect_token(')')
			self.skip_to_next()
			return TreeNode("primitive", [expr], expr.filename, expr.line_num)

	def compile_array_literal(self):                  #  array_literal        => ARRAY '(' [array_element [',' array_element]*] ')'
		fn, ln = self.cur_filename_line()
		self.expect_sequence(
			(parser.TOKEN_IDENTIFIER, KEYWORD_ARRAY),
			('(', )
		)
		args=[]
		if self.cur_token()[0] != ')':
			args.append(self.compile_array_element())
			while self.cur_token()[0] == ',':
				self.skip_to_next()
				if self.cur_token()[0] == ')':
					break
				args.append(self.compile_array_element())
		self.expect_sequence( (')', ) )
		return TreeNode('array_literal', args, fn, ln)
			
	def compile_array_element(self):                  #  array_element        => expression '=>' expression
		fn, ln = self.cur_filename_line()
		expr = [self.compile_expression()];
		if self.cur_token()[0] == '=>':
			self.skip_to_next()
			expr.append(self.compile_expression())
		return TreeNode('array_element', expr, fn, ln)


	def compile_typedef(self):                #  member_expression [static_member_access]*
		fn, ln = self.cur_filename_line()
		args=[]
		args.append(self.compile_member_expression())
		while True:
			tok = self.cur_token()
			if tok[0] == '::':
				args.append(self.compile_static_member_access())
			else:
				break
		return TreeNode("typedef", args, fn, ln)

	def compile_primitive_follower(self):     #  primitive_follower     => static_member_access | member_access | fncall | array_indexing
		tok = self.cur_token()
		follower=None
		if tok[0] == '::':
			follower = self.compile_static_member_access()
		elif tok[0] == '->':
			follower = self.compile_member_access()
		elif tok[0] == '(':
			follower = self.compile_fncall()
		elif tok[0] == '[':
			follower = self.compile_array_indexing()
		else:
			raise CompileError("Expected -> [ or (, not %s"%self.cur_token()[0])
		return follower # TreeNode('follower', follower)
	
	def compile_static_member_access(self):   #  static_member_access   => '::' member_expression
		fn, ln = self.cur_filename_line()
		self.expect_token('::')
		self.skip_to_next()
		return TreeNode('static_member_access', [self.compile_member_expression()], fn, ln)
	
	def compile_member_access(self):          #  member_access          => '->' member_expression
		fn, ln = self.cur_filename_line()
		self.expect_token('->')
		self.skip_to_next()
		return TreeNode('member_access', [self.compile_member_expression()], fn, ln)
	
	def compile_member_expression(self):      #  member_expression      => IDENTIFIER | VARIABLE | '{' expression '}'
		tok = self.cur_token()
		if tok[0] == '{':
			self.skip_to_next()
			expr = self.compile_expression()
			self.expect_token('}')
			self.skip_to_next()
			return TreeNode('member_expression', [expr], expr.filename, expr.line_num)
		else:
			if tok[0] not in (parser.TOKEN_IDENTIFIER, parser.TOKEN_VARIABLE):
				raise CompileError("Expected identifier or variable not %s"%tok[0])
			self.skip_to_next()
			return TreeNode('member_expression', [tok], tok.filename, tok.line_num)
	
	def compile_fncall(self):                 #  fncall                 => argument_list
		al = self.compile_argument_list()
		return TreeNode('fncall', [al], al.filename, al.line_num)
	
	def compile_array_indexing(self):         #  array_indexing         => '[' expression ']'
		fn, ln = self.cur_filename_line()
		self.expect_token('[')
		self.skip_to_next()
		expr= None
		if self.cur_token()[0] != ']' :
			expr = self.compile_expression()
		self.expect_token(']')
		self.skip_to_next()
		return TreeNode('array_indexing', [expr], fn, ln)
	
	def compile_if_stmt(self):           #  if_stmt           => IF '(' expression ')' stmt
		args = []
		self.expect_token(parser.TOKEN_IDENTIFIER, KEYWORD_IF)
		self.skip_to_next()
		self.expect_token('(')
		self.skip_to_next()
		args.append(self.compile_expression())
		self.expect_token(')')
		self.skip_to_next()
		args.append(self.compile_stmt())
		tok = self.cur_token()
		if tok[0] == parser.TOKEN_IDENTIFIER and tok[1] == KEYWORD_ELSE:
			self.skip_to_next()
			args.append(self.compile_stmt())
		return TreeNode("if", args, args[0].filename, args[0].line_num)
	
	def compile_classdef_stmt(self):     #  classdef_stmt   => CLASS identifier [EXTENDS identifier] '{' [classdef_block] '}'
		fn, ln = self.cur_filename_line()
		self.expect_token(parser.TOKEN_IDENTIFIER, KEYWORD_CLASS)
		self.skip_to_next()
		self.expect_token(parser.TOKEN_IDENTIFIER)
		class_name = self.cur_token()
		self.skip_to_next()
		tok = self.cur_token()
		if tok[0] == parser.TOKEN_IDENTIFIER and tok[1] == KEYWORD_EXTENDS:
			self.skip_to_next()
			self.expect_token(parser.TOKEN_IDENTIFIER)
			superclass_name = self.cur_token()
			self.skip_to_next()
		else:
			superclass_name = None
		self.expect_token('{')
		self.skip_to_next()
		classdef = self.compile_classdef_block() if self.cur_token()[0] != '}' else None
		self.expect_token('}')
		self.skip_to_next()
		return TreeNode('classdef', [class_name, superclass_name, classdef], fn, ln)
	
	def compile_classdef_block    (self):     #  classdef_block       => [const_vardef_stmt | methoddef_stmt | constdef_stmt]*
		fn, ln = self.cur_filename_line()
		args=[]
		tok = self.cur_token()
		while tok[0] != '}':
			stmt=None
			if tok[0] == parser.TOKEN_IDENTIFIER and tok[1] == KEYWORD_CONST:
				stmt = self.compile_const_vardef_stmt()
			else:
				start_i = self.i
				while tok[0] == parser.TOKEN_IDENTIFIER and tok[1] in VARDEF_DECORATORS:
					self.skip_to_next()
					tok = self.cur_token()
				
				if tok[0] == parser.TOKEN_VARIABLE:
					self.i = start_i
					stmt = self.compile_vardef_stmt()
				elif tok[0] == parser.TOKEN_IDENTIFIER and tok[1] == KEYWORD_FUNCTION:
					self.i = start_i
					stmt = self.compile_methoddef_stmt()
				else:
					raise CompileError("File:%s, line:%s, Expected stmt instead of %s"%(tok.filename, tok.line_num, ' '.join([str(x) for x in token])))
			args.append(stmt)
			# self.skip_to_next()
			tok = self.cur_token()
		return TreeNode('classdef_block', args, fn, ln)
	def compile_methoddef_stmt (self):     #  methoddef_stmt    => [vardef_decorator]* 'function' IDENTIFIER parameter_list stmt_block
		fn, ln = self.cur_filename_line()
		decorators = []
		tok = self.cur_token()
		while tok[0] == parser.TOKEN_IDENTIFIER and tok[1] in VARDEF_DECORATORS:
			decorators.append(tok[1])
			self.skip_to_next()
			tok = self.cur_token()
		self.expect_token(parser.TOKEN_IDENTIFIER, KEYWORD_FUNCTION)
		self.skip_to_next()
		self.expect_token(parser.TOKEN_IDENTIFIER)
		func_name = self.cur_token()
		self.skip_to_next()
		params = self.compile_parameter_list()
		block  = self.compile_stmt_block()
		return TreeNode('methoddef', [decorators, func_name, params, block], fn, ln)
	def compile_funcdef_stmt (self):     #  funcdef_stmt    => 'function' IDENTIFIER parameter_list stmt_block
		fn, ln = self.cur_filename_line()
		self.expect_token(parser.TOKEN_IDENTIFIER, KEYWORD_FUNCTION)
		self.skip_to_next()
		self.expect_token(parser.TOKEN_IDENTIFIER)
		func_name = self.cur_token()
		self.skip_to_next()
		params = self.compile_parameter_list()
		block  = self.compile_stmt_block()
		return TreeNode('funcdef', [func_name, params, block], fn, ln)
	def compile_parameter_list(self):         #  parameter_list       => '(' [parameter [ ',' parameter ]] ')'
		fn, ln = self.cur_filename_line()
		param_list=[]
		self.expect_token('(')
		self.skip_to_next()
		while self.cur_token()[0] != ')' :
			param_list.append(self.compile_parameter())
			if self.cur_token()[0] == ')':
				break
			else:
				self.expect_token(',')
				self.skip_to_next()
		self.skip_to_next()
		return TreeNode("parameter_list", param_list, fn, ln)
	def compile_parameter     (self):         #  parameter            => [IDENTIFIER] VARIABLE ['=' or_expression]
		fn, ln = self.cur_filename_line()
		typedef, varname, assign = None, None, None
		tok = self.cur_token()
		if tok[0] == parser.TOKEN_IDENTIFIER:
			typedef = tok
			self.skip_to_next()
		self.expect_token(parser.TOKEN_VARIABLE)
		varname = self.cur_token()
		self.skip_to_next()
		if self.cur_token()[0] == '=':
			self.skip_to_next()
			assign = self.compile_or_expression()
		return TreeNode("parameter", [typedef, varname, assign], fn, ln)
		
	def compile_vardef_stmt  (self):     #  vardef_stmt     => [vardef_decorator]+ VARIABLE ['=' or_expression] ';'
		fn, ln = self.cur_filename_line()
		decorators = []
		tok = self.cur_token()
		while tok[0] == parser.TOKEN_IDENTIFIER and tok[1] in VARDEF_DECORATORS:
			decorators.append(tok[1])
			self.skip_to_next()
			tok = self.cur_token()
		self.expect_token(parser.TOKEN_VARIABLE)
		variable = self.cur_token()
		self.skip_to_next()
		definition = None
		if self.cur_token()[0] == '=':
			self.skip_to_next()			
			definition = self.compile_or_expression()
		self.expect_token(';')
		self.skip_to_next()
		return TreeNode('vardef_stmt', [decorators, variable, definition], fn, ln)
	def compile_const_vardef_stmt(self): #  const_vardef_stmt=>const IDENTIFIER ['=' or_expression] ';'
		fn, ln = self.cur_filename_line()
		args=[]
		self.expect_token(parser.TOKEN_IDENTIFIER, KEYWORD_CONST)
		self.skip_to_next()
		self.expect_token(parser.TOKEN_IDENTIFIER)
		args.append(self.cur_token())
		self.skip_to_next()
		if self.cur_token()[0] == '=':
			self.skip_to_next()
			args.append(self.compile_or_expression())
		self.expect_token(';')
		self.skip_to_next()
		return TreeNode('const_vardef_stmt', args, fn, ln)
	def compile_vardef_decorator  (self):     #  vardef_decorator     => 'var' | 'static' | 'private' | 'public'
		pass


def compile_file(php_file):
	if type(php_file) is str:
		php_file = parser.parse_file(php_file)
	return compile_php(php_file)

def compile_php(php_tokens):
	if type(php_tokens) is str:
		php_tokens = parser.parse_php(php_tokens)
	if not isinstance(php_tokens, parser.TokenList):
		raise ArgumentError("Given argument is not php code, nor a list of tokens %r"%php_tokens)
	C = Compiler(php_tokens)
	return C.compile()


def test(*args, **kw):
	global VERBOSE
	VERBOSE = 999
	if len(args) > 0:
		kw['code'] = args[0]
	if 'filename' in kw:
		filename = kw['filename']
		print "parsing file : %r"%filename
		with file(filename) as finp:
			print finp.read()
		print "----"
		php_code = parser.parse_file(filename)
	elif 'code' in kw:
		code = kw['code']
		print "parsing php code :\n%s"%code
		print "----"
		php_code = parser.parse_php(code)
	print "----"
	print "Parsed Code:\n", php_code
	
	compiled_code = compile_php(php_code)
	print
	def print_node(node, depth=0):
		print "  "*depth, 
		if isinstance(node, TreeNode):
			print node.name
			for c in node.children:
				print_node(c, depth+1)
		else:
			print node
			
	print "Compiled Code:\n"
	print compiled_code.prepr()
	

if __name__ == '__main__':
	import sys
	if len(sys.argv) >= 2:
		test(filename=sys.argv[1])
	else:
		test(code=parser.TEST_CODE)