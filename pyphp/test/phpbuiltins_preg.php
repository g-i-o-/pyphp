<?php
echo "Unit test for Php's PCRE functions: preg_filter, preg_grep, preg_last_ error, ";
echo "preg_match_ all, preg_match, preg_quote, preg_replace_callback, preg_replace and preg_split.\n";

function test1($regex, $repstr, $subject, $limit){
    print "-------- test --------\n";
    print 'preg_replace($regex, $repstr, $subject, $limit, $count)'."\n";
    print '  << $regex   = '; var_dump($regex);
    print '  << $repstr  = '; var_dump($repstr);
    print '  << $subject = '; var_dump($subject);
    print '  << $limit   = '; var_dump($limit);
    $retval = preg_replace($regex, $repstr, $subject, $limit, $count);
    print '  >> $retval  = '; var_dump($retval);
    print '  >> $count   = '; var_dump($count);
}

test1('/fox/', 'badger', 'The lazy fox ran over the brown dog.', 1);

?>