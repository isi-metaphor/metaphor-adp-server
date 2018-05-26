#!/bin/bash

port=$1
i=1

while [ $i -le 10 ]
do
    python oldclient/client.py -g 0.0.0.0 -p $port \
        -j checkServiceFiles/en.json &
    #sleep 1
    ((i++))
done
