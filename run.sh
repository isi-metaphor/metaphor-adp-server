#!/bin/bash

port=8084
./checkService.sh $port &

while [ 1 == 1 ]
do
	#sleep 1s
	#continue
	python manage.py runserver 0.0.0.0:8084 --settings=lccsrv.settings
	SUBJECT="Aug-Eval Server Error"
	EMAIL1="amiakshp@usc.edu"
	EMAIL2="morbini@ict.usc.edu"
	EMAILMESSAGE="/tmp/emailmessage.txt"
	echo "Aug-Eval Server is down" > $EMAILMESSAGE
	process=$(ps fax|grep -e"^[ \t]*$$" -C10)
	echo "$process" >> $EMAILMESSAGE
	mail -s "$SUBJECT" "$EMAIL1" "$EMAIL2" < $EMAILMESSAGE
	sleep 30s
done
