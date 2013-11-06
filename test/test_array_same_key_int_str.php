<?php
error_reporting(E_ALL);
ini_set('display_errors', true);

$a = array();

$a[1] = 'int #1';
$a[2] = 'int #2';

$a[1.0] = 'float #1';
$a[2.0] = 'float #2';
$a[5.0] = 'float #5.0';
$a[5.1] = 'float #5.1';

$a['1'] = 'str of int #1';

$a['1.0'] = 'str of float #1';

var_dump($a);

?>
