#!/usr/bin/expect -f

set timeout 5m
set test [lindex $argv 1]
set port [lindex $argv 0]

spawn -noecho python oldclient/client.py -g 0.0.0.0 -p $port -j $test
interact

