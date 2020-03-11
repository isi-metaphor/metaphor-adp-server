#!/bin/bash

YEST_DATE=`date "+%s"`
SUBJECT=`hostname`":"`pwd`": {{STAGE}}_{{NGINX_PORT}}"
OUTPUT_FILE="/tmp/${$}-`date +%s`.tmp"

run_check() {
    ./testing/client.py -g 0.0.0.0 -p {{NGINX_PORT}} \
        -j check_service_files/$1.json > $OUTPUT_FILE
    if diff check_service_files/$1_output.json $OUTPUT_FILE; then
        sleep 20
    else
        body="Unexpected JSON response."
        process=$(ps fax | grep -e"^[ \t]*$$" -C10)
        lang_subject=$1": "$SUBJECT
        echo -e "$body\n\nPID=${$}\n$process" | mail -s "$lang_subject" $EMAILS
        sleep 5m
    fi
}

while [ 1 == 1 ]; do
    run_check "en"
    run_check "ru"
    run_check "fa"
    run_check "es"
    time_diff=$((`date "+%s"` - $YEST_DATE))
    if [ $time_diff -gt 86400 ]; then
        YEST_DATE=`date "+%s"`
        echo "" | mail -s "Running check_service.sh for $SUBJECT." $EMAILS
    fi
    sleep 5m
done
