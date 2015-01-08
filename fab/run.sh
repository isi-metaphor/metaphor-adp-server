#!/bin/bash

./checkService.sh {{NGINX_PORT}} &

SUBJECT=`hostname`":"`pwd`": {{STAGE}}_{{NGINX_PORT}}"
EMAILS="fmorbini@gmail.com morbini@ict.usc.edu"

while [ 1 == 1 ]
do
	python manage.py runserver 0.0.0.0:{{NGINX_PORT}} --settings=lccsrv.settings
	echo ""|mail -s "SERVICE DIED will restart: $SUBJECT" $EMAILS
	sleep 30s
done
