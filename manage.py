#!/usr/bin/env python
# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE


import os
import sys

ParserRunning = False
BoxerLock = True
FarsiParserRunning = False
RuParserRunning = False
EsParserRunning = False

def getEsParse():
        return EsParserRunning
def setEsParse(value):
        global EsParserRunning
        EsParserRunning = value
def getRuParse():
	return RuParserRunning
def setRuParse(value):
	global RuParserRunning
	RuParserRunning = value
def getBoxerLock():
	return BoxerLock

def setBoxerLock(val):
	BoxerLock = val


def getParse():
	return ParserRunning

def setParse(value):
	global ParserRunning
	ParserRunning = value
def getFarsiParse():
	return FarsiParserRunning

def setFarsiParse(value):
	global FarsiParserRunning
	FarsiParserRunning = value

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lcc_service.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
