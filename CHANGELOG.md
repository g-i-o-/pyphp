# CHANGELOG

## 0.2.2
  - `var_dump` now properly outputs through executer's `stdout`, instead of 
    using `print`.
  - added default `$_GET`, `$_POST` and `$_FILES` (empty) global variables to executer.
  - fixed bug where last literal text segment (right after the last `?>`) was not 
    being parsed properly.
  - fixed broken import bug in `phpbuiltins` package.

## 0.2.1
  - fixed broken import bug in `phpbuiltins` package.

## 0.2
  - fixed broken import bug in `phpbuiltins` package.
  - Added support for redirecting `stdout` in `AbstractPhpExecuter`.
  - Added usage section to readme.
  - Added changelog.
