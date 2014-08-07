#!/bin/bash

port=$(($1+0))
yest_date=`date "+%s"`
EMAIL1="amiakshp@usc.edu"
EMAIL2="morbini@ict.usc.edu"
SUBJECT="Aug-Eval Service Error"
outputFile="/tmp/outputCheckAugEval.json"
while [ 1 == 1 ]
do
	#English Check
        python oldclient/client.py -g 0.0.0.0 -p $port -j checkServiceFiles/en.json > $outputFile
	#./checkAllLanguages.sh $port checkServiceFiles/en.json
	if diff checkServiceFiles/en_output.json $outputFile; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmail.txt"
		body="Aug-Eval service for English is down! Response JSON did not match the expected JSON!"
		process=$(ps fax|grep -e"^[ \t]*$$" -C10)
		echo "$body" > $EMAIL
		echo "$process" >> $EMAIL
		mail -s "$SUBJECT" "$EMAIL1" "$EMAIL2" < $EMAIL
		sleep 5m
	fi
	
	#Russian Check
        python oldclient/client.py -g 0.0.0.0 -p $port -j checkServiceFiles/ru.json > $outputFile
	#./checkAllLanguages.sh $port checkServiceFiles/ru.json > $outputFile
	if diff checkServiceFiles/ru_output.json $outputFile; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmail.txt"
		body="Aug-Eval service for Russian is down!! Response JSON did not match the expected JSON"
		process=$(ps fax|grep -e"^[ \t]*$$" -C10)
		echo "$body" > $EMAIL
		echo "$process" >> $EMAIL
		mail -s "$SUBJECT" "$EMAIL1" "$EMAIL2" < $EMAIL
		sleep 5m
	fi
	
	#Spanish Check
        python oldclient/client.py -g 0.0.0.0 -p $port -j checkServiceFiles/es.json > $outputFile
	#./checkAllLanguages.sh $port checkServiceFiles/es.json > $outputFile
	if diff checkServiceFiles/es_output.json $outputFile; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmail.txt"
		body="Aug-Eval service for Spanish is down!! Response JSON did not match the expected JSON"
		process=$(ps fax|grep -e"^[ \t]*$$" -C10)
		echo "$body" > $EMAIL
		echo "$process" >> $EMAIL
		mail -s "$SUBJECT" "$EMAIL1" "$EMAIL2" < $EMAIL
		sleep 5m
	fi

	#Farsi Check
        python oldclient/client.py -g 0.0.0.0 -p $port -j checkServiceFiles/fa.json > $outputFile
	#./checkAllLanguages.sh $port checkServiceFiles/fa.json > $outputFile
	if diff checkServiceFiles/fa_output.json $outputFile; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmail.txt"
		body="Aug-Eval service for Farsi is down!! Response JSON did not match the expected JSON"
		process=$(ps fax|grep -e"^[ \t]*$$" -C10)
		echo "$body" > $EMAIL
		echo "$process" >> $EMAIL
		mail -s "$SUBJECT" "$EMAIL1" "$EMAIL2" < $EMAIL
		sleep 5m
	fi
	time_diff=$((`date "+%s"` - $yest_date)) 
	if [ $time_diff -gt 86400 ]; then
		yest_date=`date "+%s"`
		EMAIL="/tmp/serviceEmail.txt"
		echo "CheckServiceScript for Aug-Eval is running!" > $EMAIL
		mail -s "checkServiceScript for Aug-Eval is Running today!" "$EMAIL1" "$EMAIL2" < $EMAIL
	fi
	sleep 5m
done
