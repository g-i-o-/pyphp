<?php

function a($a, $b){ echo $a, $b;}

a(1);
$b=2;
echo split('1,2,3', ',');
trigger_error('msg1 notice');
trigger_error('msg1 E_USER_DEPRECATED',E_USER_DEPRECATED);
trigger_error('msg1 warning', E_USER_WARNING);
trigger_error('msg1 error', E_USER_ERROR);
echo "done!\n"
?>