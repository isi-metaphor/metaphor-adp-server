#!/bin/bash

# A stress test for the server.

# Usage: ./concurrentCheck.sh 8000

port=$1
i=1

while [ $i -le 10 ]
do
    ./client.py -g localhost -p $port -j ../checkServiceFiles/en.json &
    # sleep 1
    ((i++))
done
