#!/bin/bash

./check_service.sh &

SUBJECT="$(hostname):$(pwd): {{STAGE}}_{{NGINX_PORT}}"

while [ 1 == 1 ]
do
    python2.7 manage.py runserver 0.0.0.0:{{NGINX_PORT}} \
           --settings=lccsrv.settings
    echo "" | mail -s "SERVICE DIED will restart: $SUBJECT" $EMAILS
    sleep 30s
done
