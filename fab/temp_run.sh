#!/bin/bash

python2.7 manage.py runserver 0.0.0.0:{{NGINX_PORT}} --settings=adpsrv.settings
