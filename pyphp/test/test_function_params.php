<?php

function d($x, $y){
    echo $x, ' = '; var_dump($y);
}

function test1($p1, $p2 = 1){
    echo "===\n";
    d('$p1', $p1);
    d('$p2', $p2);
    echo "===\n";
}

function test2($p1, $p2 = 0){
    echo "===\n";
    d('$p1', $p1);
    d('$p2', $p2);
    echo "===\n";
}

function test3($p1, $p2 = null){
    echo "===\n";
    d('$p1', $p1);
    d('$p2', $p2);
    echo "===\n";
}

echo "test1\n";
test1(1);
test1(1, 2);

echo "test2\n";
test2(1);
test2(1, 2);

echo "test3\n";
test3(1);
test3(1, 2);


?>