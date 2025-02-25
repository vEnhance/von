sub von_run { return system("bash -i '$_[0].von'"); }
add_cus_dep("von", "out", 0, "von_run");

# vim: ft=perl
