#!/usr/bin/env python2.7
# coding: utf-8

# Copyright (C) University of Southern California (https://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <https://nlg.isi.edu>
# For more information, see README.md
# For license information, see LICENSE

import os
import sys


PARSER_RUNNING = {'FA': False, 'ES': False, 'RU': False, 'EN': False}
PARSER_LOCK = {'FA': True, 'ES': True, 'RU': True, 'EN': True}
PARSER_FLAG = True


def get_parser_flag():
    global PARSER_FLAG
    # print "Value of PARSER_FLAG is", PARSER_FLAG
    return PARSER_FLAG


def set_parser_flag(value):
    global PARSER_FLAG
    PARSER_FLAG = value
    # print "Parser Flag value set to", value


def get_parser_status(language):
    return PARSER_RUNNING[language]


def set_parser_status(language, value):
    global PARSER_RUNNING
    PARSER_RUNNING[language] = value


def get_parser_lock(language):
    return PARSER_LOCK[language]


def set_parser_lock(language, value):
    global PARSER_LOCK
    PARSER_LOCK[language] = value


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lccsrv.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
