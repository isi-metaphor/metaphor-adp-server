# !/bin/bash

port=$1
echo $port
while [ 1 == 1 ]
do
	#English Check
	./checkAllLanguages.sh $port checkServiceFiles/en.json > /tmp/outputCheckDev.json
	if diff checkServiceFiles/en_output.json /tmp/outputCheckDev.json; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmailDev.txt"
		echo "Dev service for English is down!!" > $EMAIL
		mail -s "Dev Service Error" "amiakshp@usc.edu" < $EMAIL
		sleep 5m
	fi
	
	#Russian Check
	./checkAllLanguages.sh $port checkServiceFiles/ru.json > /tmp/outputCheckDev.json
	if diff checkServiceFiles/ru_output.json /tmp/outputCheckDev.json; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmailDev.txt"
		echo "Dev service for Russian is down!!" > $EMAIL
		mail -s "Dev Service Error" "amiakshp@usc.edu" < $EMAIL
		sleep 5m
	fi

	#Spanish Check
	./checkAllLanguages.sh $port checkServiceFiles/es.json > /tmp/outputCheckDev.json
	if diff checkServiceFiles/es_output.json /tmp/outputCheckDev.json; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmailDev.txt"
		echo "Dev service for Spanish is down!!" > $EMAIL
		mail -s "Dev Service Error" "amiakshp@usc.edu" < $EMAIL
		sleep 5m
	fi
	

	#Farsi Check
	./checkAllLanguages.sh $port checkServiceFiles/fa.json > /tmp/outputCheckDev.json
	if diff checkServiceFiles/fa_output.json /tmp/outputCheckDev.json; then
		sleep 20
	else
		EMAIL="/tmp/serviceEmailDev.txt"
		echo "Dev service for Farsi is down!!" > $EMAIL
		mail -s "Dev Service Error" "amiakshp@usc.edu" < $EMAIL
		sleep 5m
	fi

	#sleep 5m 
done
