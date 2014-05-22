#!/bin/bash

while [ 1 == 1 ]
do
	python manage.py runserver 0.0.0.0:8081 --settings=lccsrv.settings
	SUBJECT="Dev Server Error"
	EMAIL="amiakshp@usc.edu"
	EMAILMESSAGE="/tmp/emailmessage.txt"
	echo "Dev Server is down" > $EMAILMESSAGE
	mail -s "$SUBJECT" "$EMAIL" < $EMAILMESSAGE
	sleep 30s
done
