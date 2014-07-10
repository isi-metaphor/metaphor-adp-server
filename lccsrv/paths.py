# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

import os
import sys
import logging


logger = logging.getLogger("pipeline")


METAPHOR_DIR        =  "/mnt/metaphor"
HENRY_DIR           =  "/mnt/deploy/henry-n700"
BOXER_DIR           =  "/mnt/deploy/boxer"
TMP_DIR             =  "/home/jonmay/lcc/tmp"
GUROBI_HOME         =  "/mnt/deploy/gurobi511/linux64/"
GRB_LICENSE_FILE    =  "/mnt/deploy/gurobi.lic"
CPLUS_INCLUDE_PATH  =  "/usr/include/python2.7/:/mnt/deploy/gurobi511/linux64/include"
PATH                =  ".:${TEAM_LOCAL}/bin:${TEAM_PUBLIC}/bin:${PATH}:/usr/sbin:/sbin:/usr/bin:${GUROBI_HOME}/bin"
LD_LIBRARY_PATH     =  ":${GUROBI_HOME}/lib/:${LD_LIBRARY_PATH}"
LIBRARY_PATH        =  "${GUROBI_HOME}/lib"
UPLOADS_DIR         =  "/mnt/deploy/kbs"

FARSI_PIPELINE      =  os.path.join(METAPHOR_DIR, "pipelines/Farsi/LF_Pipeline")
SPANISH_PIPELINE    =  os.path.join(METAPHOR_DIR, "pipelines/Spanish/run_spanish.sh")
RUSSIAN_PIPELINE    =  os.path.join(METAPHOR_DIR, "pipelines/Russian/run_russian.sh")

BOXER2HENRY         =  os.path.join(METAPHOR_DIR, "pipelines/English/Boxer2Henry.py")
PARSER2HENRY        =  os.path.join(METAPHOR_DIR, "pipelines/common/IntParser2Henry.py")

KBS_DIR             =  os.path.join(METAPHOR_DIR, "KBs")

EN_KBPATH           =  os.path.join(KBS_DIR, "English/English_compiled_KB.da")
ES_KBPATH           =  os.path.join(KBS_DIR, "Spanish/Spanish_compiled_KB.da")
RU_KBPATH           =  os.path.join(KBS_DIR, "Russian/Russian_compiled_KB.da")
FA_KBPATH           =  os.path.join(KBS_DIR, "Farsi/Farsi_compiled_KB.da")

CODE_RU             =  os.path.join(METAPHOR_DIR, "pipelines/Russian/")
CODE_EN             =  os.path.join(METAPHOR_DIR, "pipelines/English/")
CODE_ES             =  os.path.join(METAPHOR_DIR, "pipelines/Spanish/")
CODE_FA             =  os.path.join(METAPHOR_DIR, "pipelines/Farsi/")
CODE_COMMON         =  os.path.join(METAPHOR_DIR, "pipelines/common/")


sys.path.extend([CODE_RU, CODE_EN, CODE_ES, CODE_FA, CODE_COMMON])


logger.info("METAPHOR_DIR:          %r" % os.environ.get("METAPHOR_DIR"))
logger.info("HENRY_DIR:             %r" % os.environ.get("HENRY_DIR"))
logger.info("BOXER_DIR:             %r" % os.environ.get("BOXER_DIR"))
logger.info("TMP_DIR:               %r" % os.environ.get("TMP_DIR"))
logger.info("GUROBI_HOME:           %r" % os.environ.get("GUROBI_HOME"))
logger.info("GRB_LICENSE_FILE:      %r" % os.environ.get("GRB_LICENSE_FILE"))
logger.info("CPLUS_INCLUDE_PATH:    %r" % os.environ.get("CPLUS_INCLUDE_PATH"))
logger.info("PATH:                  %r" % os.environ.get("PATH"))
logger.info("LD_LIBRARY_PATH:       %r" % os.environ.get("LD_LIBRARY_PATH"))
logger.info("LIBRARY_PATH:          %r" % os.environ.get("LIBRARY_PATH"))

logger.info("FARSI_PIPELINE:        %s" % FARSI_PIPELINE)
logger.info("SPANISH_PIPELINE:      %s" % SPANISH_PIPELINE)
logger.info("RUSSIAN_PIPELINE:      %s" % RUSSIAN_PIPELINE)
logger.info("PARSER2HENRY:          %s" % PARSER2HENRY)
logger.info("EN_KBPATH:             %s" % EN_KBPATH)
logger.info("ES_KBPATH:             %s" % ES_KBPATH)
logger.info("RU_KBPATH:             %s" % RU_KBPATH)
logger.info("FA_KBPATH:             %s" % FA_KBPATH)
logger.info("CODE_RU:               %s" % CODE_RU)
logger.info("CODE_EN:               %s" % CODE_EN)
logger.info("CODE_ES:               %s" % CODE_ES)
logger.info("CODE_FA:               %s" % CODE_FA)
logger.info("CODE_COMMON:           %s" % CODE_COMMON)