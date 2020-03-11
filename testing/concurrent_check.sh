#!/bin/bash

# A stress test for the server.

# Usage: ./concurrent_check.sh 8000

port=$1
i=1

while [ $i -le 10 ]; do
    ./client.py -g localhost -p $port -j ../check_service_files/en.json &
    # sleep 1
    ((i++))
done
