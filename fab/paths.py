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


METAPHOR_DIR        =  "{{PIPELINE_CONFIG.METAPHOR_DIR}}"
HENRY_DIR           =  "{{PIPELINE_CONFIG.HENRY_DIR}}"
BOXER_DIR           =  "{{PIPELINE_CONFIG.BOXER_DIR}}"
TMP_DIR             =  "{{PIPELINE_CONFIG.TMP_DIR}}"
GUROBI_HOME         =  "{{PIPELINE_CONFIG.GUROBI_HOME}}"
GRB_LICENSE_FILE    =  "{{PIPELINE_CONFIG.GRB_LICENSE_FILE}}"
CPLUS_INCLUDE_PATH  =  "{{PIPELINE_CONFIG.CPLUS_INCLUDE_PATH}}"
PATH                =  "{{PIPELINE_CONFIG.PATH}}"
LD_LIBRARY_PATH     =  "{{PIPELINE_CONFIG.LD_LIBRARY_PATH}}"
LIBRARY_PATH        =  "{{PIPELINE_CONFIG.LIBRARY_PATH}}"

FARSI_PIPELINE      =  os.path.join(METAPHOR_DIR, "/pipelines/Farsi/LF_Pipeline")
SPANISH_PIPELINE    =  os.path.join(METAPHOR_DIR, "/pipelines/Spanish/run_spanish.sh")
RUSSIAN_PIPELINE    =  os.path.join(METAPHOR_DIR, "/pipelines/Russian/run_russian.sh")

BOXER2HENRY         =   os.path.join(METAPHOR_DIR, "/pipelines/English/Boxer2Henry.py")
PARSER2HENRY        =   os.path.join(METAPHOR_DIR, "/pipelines/common/IntParser2Henry.py")

EN_KBPATH           =   os.path.join(METAPHOR_DIR, "/KBs/English/English_compiled_KB.da")
ES_KBPATH           =   os.path.join(METAPHOR_DIR, "/KBs/Spanish/Spanish_compiled_KB.da")
RU_KBPATH           =   os.path.join(METAPHOR_DIR, "/KBs/Russian/Russian_compiled_KB.da")
FA_KBPATH           =   os.path.join(METAPHOR_DIR, "/KBs/Farsi/Farsi_compiled_KB.da")

CODE_RU             =   os.path.join(METAPHOR_DIR, "/pipelines/Russian/")
CODE_EN             =   os.path.join(METAPHOR_DIR, "/pipelines/English/")
CODE_ES             =   os.path.join(METAPHOR_DIR, "/pipelines/Spanish/")
CODE_FA             =   os.path.join(METAPHOR_DIR, "/pipelines/Farsi/")
CODE_COMMON         =   os.path.join(METAPHOR_DIR, "/pipelines/common/")


sys.path.extend([CODE_RU, CODE_EN, CODE_ES, CODE_FA, CODE_COMMON])


logger.info("METAPHOR_DIR:          %s" % METAPHOR_DIR)
logger.info("HENRY_DIR:             %s" % HENRY_DIR)
logger.info("BOXER_DIR:             %s" % BOXER_DIR)
logger.info("TMP_DIR:               %s" % TMP_DIR)
logger.info("GUROBI_HOME:           %s" % GUROBI_HOME)
logger.info("GRB_LICENSE_FILE:      %s" % GRB_LICENSE_FILE)
logger.info("CPLUS_INCLUDE_PATH:    %s" % CPLUS_INCLUDE_PATH)
logger.info("PATH:                  %s" % PATH)
logger.info("LD_LIBRARY_PATH:       %s" % LD_LIBRARY_PATH)
logger.info("LIBRARY_PATH:          %s" % LIBRARY_PATH)
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
