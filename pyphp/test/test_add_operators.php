<?php

function test($h, $val){
    echo $h, ' = '; var_dump($val);
}

$a = array(1=>1,'b'=>3, 'o'=>'a', 10 => 'a10');
$b = array(5=>5,'c'=>'asd', 'o'=>'b', 10 => 'b10');


test('$a', $a);
test('$b', $a);

test('1 + 0', 1 + 0);
test('1 + "40 rabbits"', 1 + "40 rabbits");
test('$a + $b', $a + $b);
test('1 + $a', 1 + $a);
test('"1 d" + $a', "1 d" + $a);

?>