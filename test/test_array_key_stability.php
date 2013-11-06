<?php

$a = array('key 0', 'key 1', 5=>'explicit key 5', 'implicit key 6', 'strkey1' => 'strkey #1', 'key 7', 'strkey2' => 'str key #2', 'key 8');

function p($a){
   $i=0;
   echo "array(";
   foreach($a as $k => $v){
      echo ($i++ > 0 ? ", " : "");
      echo "$k=>$v";
   }
   echo ");\n";
}

p($a);
$a[] = 'appended_key #1';
p($a);
array_push($a, 'appended_key #1');
p($a);
array_pop($a);
p($a);
array_unshift($a, 'unshifted key #1');
p($a);
array_unshift($a, 'unshifted key #2');
p($a);
array_push($a, 'pushed key');
p($a);
$a[] = 'appended_key #2';
p($a);


?>
