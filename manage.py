#!/usr/bin/env python
# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE


import os
import sys

ParserRunning = {'FA':False, 'ES':False, 'RU':False, 'EN':False}
ParserLock = {'FA':True, 'ES':True, 'RU':True, 'EN':True}
ParserFlag =True 

def getParserFlag():
    global ParserFlag
    #print "Value of ParserFlag is " + str(ParserFlag)
    return ParserFlag

def setParserFlag(value):
    global ParserFlag
    ParserFlag = value
    #print "Parser Flag value set to " + str(value)

def getParserStatus(language):
    return ParserRunning[language]

def setParserStatus(language, value):
    global ParserRunning
    ParserRunning[language] = value

def getParserLock(language):
    return ParserLock[language]

def setParserLock(language, value):
    global ParserLock
    ParserLock[language] = value

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lcc-dev.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

	
