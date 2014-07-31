# !/bin/bash

port=$1
yest_date=`date "+%s"`
EMAIL1="amiakshp@usc.edu"
EMAIL2="morbini@ict.usc.edu"
SUBJECT="Dev Parser Alive Service Error"
outputFile="/tmp/outputCheckDevParserAlive.json"

while [ 1 == 1 ]
do
	#English Check
	./checkAllLanguages.sh $port checkServiceFiles/en.json > $outputFile
	if diff checkServiceFiles/en_output.json $outputFile; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmailDev.txt"
		body="Dev service for English is down! Response JSON did not match the expected JSON!"
		process=$(ps fax|grep -e"^[ \t]*$$" -C10)
		echo "$body" > $EMAIL
		echo "$process" >> $EMAIL
		mail -s "SUBJECT" "$EMAIL1" "$EMAIL2" < $EMAIL
		sleep 5m
	fi
	
	#Russian Check
	./checkAllLanguages.sh $port checkServiceFiles/ru.json > $outputFile
	if diff checkServiceFiles/ru_output.json $outputFile; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmailDev.txt"
		body="Dev service for Russian is down!! Response JSON did not match the expected JSON"
		process=$(ps fax|grep -e"^[ \t]*$$" -C10)
		echo "$body" > $EMAIL
		echo "$process" >> $EMAIL
		mail -s "SUBJECT" "$EMAIL1" "$EMAIL2" < $EMAIL
		sleep 5m
	fi
	
	#Spanish Check
	./checkAllLanguages.sh $port checkServiceFiles/es.json > $outputFile
	if diff checkServiceFiles/es_output.json $outputFile; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmailDev.txt"
		body="Dev service for Spanish is down!! Response JSON did not match the expected JSON"
		process=$(ps fax|grep -e"^[ \t]*$$" -C10)
		echo "$body" > $EMAIL
		echo "$process" >> $EMAIL
		mail -s "SUBJECT" "$EMAIL1" "$EMAIL2" < $EMAIL
		sleep 5m
	fi

	#Farsi Check
	./checkAllLanguages.sh $port checkServiceFiles/fa.json > $outputFile
	if diff checkServiceFiles/fa_output.json $outputFile; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmailDev.txt"
		body="Dev service for Farsi is down!! Response JSON did not match the expected JSON"
		process=$(ps fax|grep -e"^[ \t]*$$" -C10)
		echo "$body" > $EMAIL
		echo "$process" >> $EMAIL
		mail -s "SUBJECT" "$EMAIL1" "$EMAIL2" < $EMAIL
		sleep 5m
	fi
	time_diff=$((`date "+%s"` - $yest_date)) 
	if [ $time_diff -gt 86400 ]; then
		yest_date=`date "+%s"`
		EMAIL="/tmp/serviceEmailDev.txt"
		echo "CheckServiceScript is running!" > $EMAIL
		mail -s "checkServiceScript is Running today!" "$EMAIL1" "$EMAIL2" < $EMAIL
	fi
	#sleep 5m 
done
