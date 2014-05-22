#!/bin/bash

while [ 1 == 1 ]
do
	python manage.py runserver 0.0.0.0:8081 --settings=lccsrv.settings
done
