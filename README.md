pyphp
=====

Php parser, compiler and interpreter for python


Usage
----

###Executing php code
You can execute php code using the `pyphp.executer` module. The `execute_file` reads a php file and executes it, while `execute_php` executes given php code.


- To run a php script:
 ```python
 import pyphp.executer
 pyphp.executer.execute_file('my_php_code.php')
 ```

 my_php_code.php contents:
 ```php
 Hello <?php echo "World\n";?>
 ```

- To run php code
 ```python
 import pyphp.executer

 phpcode = r'Hello <?php echo "World.\n"; ?>';

 pyphp.executer.execute_php(phpcode)
 ```
 output:
 ```
 Hello World.
 ```
- You can redirect the script's output to any file-like object, such as `StringIO`
  ```python
  import pyphp.executer
  import StringIO

  stdout = StringIO.StringIO()
  phpcode = r'Hello <?php echo "World.\n"; ?>';

  pyphp.executer.execute_php(phpcode, stdout=stdout)

  print repr(`stdout.getvalue())
  ```
  output:
  ```
  'Hello World.\n'
  ```

- You can run the php file directly by using the module as a script:
 ```sh
    python pyphph/executer.py phpscript.php arg1 arg2 ...
 ```





###Using the parser
The parser breaks up the php code into a list of tokens.

- This will parse a php file in the same directory and return it as a list of tokens.
 ``` python
 import pyphp.parser
 token_list = pyphp.parser.parse_file("my_php_code.php")
 ```


- You can also parse the php code directly:
 ``` python
 import pyphp.parser

 phpcode = r'Hello <?php echo "World.\n";?>';

 token_list = pyphp.parser.parse_php(phpcode)
 ```

- `token_list` would be a list like this:
 ```
 [Token['DIRECT_OUTPUT', 'Hello '],
  Token['WS'],
  Token['IDENTIFIER', 'echo'],
  Token['WS'],
  Token['STRING', 'World\n'],
  Token[';']]
 ```
 this token list can then be fed to the compiler to generate a syntax tree.

###Using the compiler
The compiler takes a list of tokens a creates a syntax tree representing the code

- This will compile a php file in the same directory and return it as a syntax tree.
``` python
import pyphp.compiler
syntax_tree = pyphp.compiler.compile_file("my_php_code.php")
```

- You can also compile the php code :
``` python
import pyphp.compiler

phpcode = r'Hello <?php echo "World.\n";?>';

syntax_tree = pyphp.compiler.compile_php(phpcode)
```

- Or compile the list of tokens directly:
``` python
import pyphp.parser
import pyphp.compiler

phpcode = r'Hello <?php echo "World.\n";?>';

token_list = pyphp.parser.parse_php(phpcode)

syntax_tree = pyphp.compiler.compile_php(token_list)
```

- `syntax_tree` would be a `TreeNode` object like this:
```
TreeNode<php_file>[
    TreeNode<direct_output>['Hello '],
    TreeNode<echo>[
        TreeNode<primitive>[
            Token['STRING', 'World\n']
        ]
    ]
]
```
    This `TreeNode` object can then be fed to `execute_php` to run the code.


###PHP Library support
Currently, only a minimal set of PHP's language features and built in library is supported, but the plan is to support as most of it as possible.

Language features not supported yet are namespaces, anonymous functions, lots of other stuff.

Below is the official subset of PHP's built in features currently supported.


| name | description | supported |
|-----|----|-----|
| `true`           | true literal  | yes         |
| `false`          | false literal | yes         |
| `null`           | null literal  | yes         |
| `E_ERROR`             | error constant | yes |
| `E_WARNING`           | error constant | yes |
| `E_PARSE`             | error constant | yes |
| `E_NOTICE`            | error constant | yes |
| `E_CORE_ERROR`        | error constant | yes |
| `E_CORE_WARNING`      | error constant | yes |
| `E_COMPILE_ERROR`     | error constant | yes |
| `E_COMPILE_WARNING`   | error constant | yes |
| `E_USER_ERROR`        | error constant | yes |
| `E_USER_WARNING`      | error constant | yes |
| `E_USER_NOTICE`       | error constant | yes |
| `E_STRICT`            | error constant | yes |
| `E_RECOVERABLE_ERROR` | error constant | yes |
| `E_DEPRECATED`        | error constant | yes |
| `E_USER_DEPRECATED`   | error constant | yes |
| `E_ALL`               | error constant | yes |
| `isset`         | Checks if a variable is set | yes |
| `empty`          | checks if a variable is empty | yes |
| `die`            | outputs to stdout and halts execution | yes |
| `defined`        | returns whether a constant is defined or not | yes |
| `require_once`   | requires a php script once | yes |
| `require`        | requires a php script | yes |
| `include_once`   | includes a php script once | yes |
| `include`        | includes a php script | yes |
| `var_dump`       | dumps a variable to stdout | yes |
| `ini_set`        | modifies settings derived from php.ini | no-op |
| `error_reporting` | modifies error reporting level| yes |
|`date_default_timezone_set`|sets default datetime zone| no-op|
