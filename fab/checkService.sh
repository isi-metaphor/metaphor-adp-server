#!/bin/bash

runCheck() {
        python oldclient/client.py -g 0.0.0.0 -p $port -j checkServiceFiles/$1.json > $outputFile
	if diff checkServiceFiles/$1_output.json $outputFile; then
		sleep 20
	else
		body="Response JSON did not match the expected JSON!"
		process=$(ps fax|grep -e"^[ \t]*$$" -C10)
		langSubject=$1": "$SUBJECT
		echo "$body\n$process" | mail -s \"$langSubject\" $EMAILS
		sleep 5m
	fi
}

port=$(($1+0))
yest_date=`date "+%s"`
EMAILS="fmorbini@gmail.com morbini@ict.usc.edu"
SUBJECT=`hostname`":"`pwd`": {{STAGE}}_{{NGINX_PORT}}"
outputFile="/tmp/outputCheckAugEval.json"
while [ 1 == 1 ]
do
    runCheck "en"
    runCheck "ru"
    runCheck "fa"
    runCheck "es"
    time_diff=$((`date "+%s"` - $yest_date)) 
    if [ $time_diff -gt 86400 ]; then
	yest_date=`date "+%s"`
	echo ""|mail -s \""checkServiceScript for "$SUBJECT" is running."\" "$EMAILS"
    fi
    sleep 5m
done
