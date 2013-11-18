<?php

echo "This test will die in mid script...\n";

function test(){
    echo "Dying in 3, 2, 1...\n";
    die("These are my last words....\n");
}

function test2(){
    echo "This should not be executed.\n";
}


test();
test2();

?>