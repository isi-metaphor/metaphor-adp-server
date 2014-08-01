#!/bin/bash

./checkService.sh 8083 &

while [ 1 == 1 ]
do
	python manage.py runserver 0.0.0.0:8083 --settings=lccsrv.settings
	SUBJECT="Dev-Parser-Alive Server Error"
	EMAIL1="amiakshp@usc.edu"
	EMAIL2="morbini@ict.usc.edu"
	EMAILMESSAGE="/tmp/emailmessage.txt"
	echo "Dev-Parser-Alive Server is down" > $EMAILMESSAGE
	process=$(ps fax|grep -e"^[ \t]*$$" -C10)
	echo "$process" >> $EMAILMESSAGE
	mail -s "$SUBJECT" "$EMAIL1" "$EMAIL2" < $EMAILMESSAGE
	sleep 30s
done
