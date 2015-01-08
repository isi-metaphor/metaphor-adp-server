#!/usr/bin/env python
# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

import json
import httplib
import logging

from optparse import OptionParser


logging.basicConfig(level=logging.INFO)


parser = OptionParser()
parser.add_option("-p", "--port",       dest="port",            type=int, default=8000)
parser.add_option("-g", "--hostname",   dest="hostname",        type=str, default="localhost")
parser.add_option("-j", "--json-file",  dest="json_filename",   type=str)

options, args = parser.parse_args()


if not options.json_filename:
    logging.error("Must supply a JSON file to send to the web service")
    exit(1)

# Verify that the JSON file is valid JSON
json_string = None
try:
    with open(options.json_filename, 'r') as json_file:
        json_obj = json.load(json_file)
        json_string = json.dumps(json_obj, indent=3)
except ValueError:
    logging.error("JSON file contained invalid json.")


logging.info("Sending JSON to port {0} on {1}...".format(options.port, options.hostname))

# Create the connection with the neccessary headers
headers = {
    "Accept":       "application/json",
    "Content-type": "application/json"
}

conn = httplib.HTTPConnection(options.hostname, options.port)
conn.request("POST", "/annotateDocument", json_string, headers)

# Process the response
response = conn.getresponse()
if response.status != 200:
    logging.error("Returned back a bad response code from the server: {0} {1}".format(
        response.status, response.reason))
else:
    response_body = response.read()
    # Verify that the return JSON is valid JSON
    try:
        json_obj = json.loads(response_body)
        json_string = json.dumps(json_obj, indent=3)
        print json_string
    except ValueError:
        parser.error("The reply JSON was in invalid JSON format.")

# Close off the connection
conn.close()
