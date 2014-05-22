#!/bin/bash

while [ 1 == 1 ]
do
	python manage.py runserver 0.0.0.0:8081 --settings=lccsrv.settings
	SUBJECT="Dev Server Error"
	EMAIL1="amiakshp@usc.edu"
	EMAIL2="amiparik@isi.edu"
	EMAIL3="morbini@ict.usc.edu"
	EMAILMESSAGE="/tmp/emailmessage.txt"
	echo "Dev Server is down" > $EMAILMESSAGE
	mail -s "$SUBJECT" "$EMAIL1" "$EMAIL2" "$EMAIL3" < $EMAILMESSAGE
	sleep 30s
done
