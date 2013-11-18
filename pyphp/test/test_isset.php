<?php

function d($a, $b){
    echo $a, ' = ' ; var_dump($b);
}

echo "test1\n";
d('isset($a)', isset($a));
echo "test2\n";
$b=array(1=>1,'w'=>4);
d('$b', $b);
d('isset($b)', isset($b));
d('isset($b[1])', isset($b[1]));
d('isset($b[30])', isset($b[30]));
echo "test3\n";
d('isset($c[30])', isset($c[30]));


?>