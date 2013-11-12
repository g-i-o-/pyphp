<?php
function t($x){
	echo " : $x:true : ";
	return true;
}
function f($x){
	echo " : $x:false : ";
	return false;
}

echo "a && b :\n";
echo "  - t && t = "; var_dump(t("a") && t("b"));
echo "  - t && f = "; var_dump(t("a") && f("b"));
echo "  - f && t = "; var_dump(f("a") && t("b"));
echo "  - f && f = "; var_dump(f("a") && f("b"));

echo "a && b && c:\n";
echo "  - t && t && t= "; var_dump(t("a") && t("b") && t("c"));
echo "  - t && f && t= "; var_dump(t("a") && f("b") && t("c"));
echo "  - f && t && t= "; var_dump(f("a") && t("b") && t("c"));
echo "  - f && f && t= "; var_dump(f("a") && f("b") && t("c"));
echo "  - t && t && f= "; var_dump(t("a") && t("b") && f("c"));
echo "  - t && f && f= "; var_dump(t("a") && f("b") && f("c"));
echo "  - f && t && f= "; var_dump(f("a") && t("b") && f("c"));
echo "  - f && f && f= "; var_dump(f("a") && f("b") && f("c"));

echo "a and b :\n";
echo "  - t and t = "; var_dump(t("a") and t("b"));
echo "  - t and f = "; var_dump(t("a") and f("b"));
echo "  - f and t = "; var_dump(f("a") and t("b"));
echo "  - f and f = "; var_dump(f("a") and f("b"));

echo "a and b and c:\n";
echo "  - t and t and t= "; var_dump(t("a") and t("b") and t("c"));
echo "  - t and f and t= "; var_dump(t("a") and f("b") and t("c"));
echo "  - f and t and t= "; var_dump(f("a") and t("b") and t("c"));
echo "  - f and f and t= "; var_dump(f("a") and f("b") and t("c"));
echo "  - t and t and f= "; var_dump(t("a") and t("b") and f("c"));
echo "  - t and f and f= "; var_dump(t("a") and f("b") and f("c"));
echo "  - f and t and f= "; var_dump(f("a") and t("b") and f("c"));
echo "  - f and f and f= "; var_dump(f("a") and f("b") and f("c"));

echo "a || b :\n";
echo "  - t || t = "; var_dump(t("a") || t("b"));
echo "  - t || f = "; var_dump(t("a") || f("b"));
echo "  - f || t = "; var_dump(f("a") || t("b"));
echo "  - f || f = "; var_dump(f("a") || f("b"));

echo "a || b || c:\n";
echo "  - t || t || t= "; var_dump(t("a") || t("b") || t("c"));
echo "  - t || f || t= "; var_dump(t("a") || f("b") || t("c"));
echo "  - f || t || t= "; var_dump(f("a") || t("b") || t("c"));
echo "  - f || f || t= "; var_dump(f("a") || f("b") || t("c"));
echo "  - t || t || f= "; var_dump(t("a") || t("b") || f("c"));
echo "  - t || f || f= "; var_dump(t("a") || f("b") || f("c"));
echo "  - f || t || f= "; var_dump(f("a") || t("b") || f("c"));
echo "  - f || f || f= "; var_dump(f("a") || f("b") || f("c"));

echo "a or b :\n";
echo "  - t or t = "; var_dump(t("a") or t("b"));
echo "  - t or f = "; var_dump(t("a") or f("b"));
echo "  - f or t = "; var_dump(f("a") or t("b"));
echo "  - f or f = "; var_dump(f("a") or f("b"));

echo "a or b or c:\n";
echo "  - t or t or t= "; var_dump(t("a") or t("b") or t("c"));
echo "  - t or f or t= "; var_dump(t("a") or f("b") or t("c"));
echo "  - f or t or t= "; var_dump(f("a") or t("b") or t("c"));
echo "  - f or f or t= "; var_dump(f("a") or f("b") or t("c"));
echo "  - t or t or f= "; var_dump(t("a") or t("b") or f("c"));
echo "  - t or f or f= "; var_dump(t("a") or f("b") or f("c"));
echo "  - f or t or f= "; var_dump(f("a") or t("b") or f("c"));
echo "  - f or f or f= "; var_dump(f("a") or f("b") or f("c"));

echo "a xor b :\n";
echo "  - t xor t = "; var_dump(t("a") xor t("b"));
echo "  - t xor f = "; var_dump(t("a") xor f("b"));
echo "  - f xor t = "; var_dump(f("a") xor t("b"));
echo "  - f xor f = "; var_dump(f("a") xor f("b"));

echo "a xor b xor c:\n";
echo "  - t xor t xor t= "; var_dump(t("a") xor t("b") xor t("c"));
echo "  - t xor f xor t= "; var_dump(t("a") xor f("b") xor t("c"));
echo "  - f xor t xor t= "; var_dump(f("a") xor t("b") xor t("c"));
echo "  - f xor f xor t= "; var_dump(f("a") xor f("b") xor t("c"));
echo "  - t xor t xor f= "; var_dump(t("a") xor t("b") xor f("c"));
echo "  - t xor f xor f= "; var_dump(t("a") xor f("b") xor f("c"));
echo "  - f xor t xor f= "; var_dump(f("a") xor t("b") xor f("c"));
echo "  - f xor f xor f= "; var_dump(f("a") xor f("b") xor f("c"));

?>