#!/bin/bash

./checkService.sh &

SUBJECT=`hostname`":"`pwd`": {{STAGE}}_{{NGINX_PORT}}"

while [ 1 == 1 ]
do
	python manage.py runserver 0.0.0.0:{{NGINX_PORT}} --settings=lccsrv.settings
	echo ""|mail -s "SERVICE DIED will restart: $SUBJECT" $EMAILS
	sleep 30s
done
