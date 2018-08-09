# coding: utf-8

# Copyright (C) University of Southern California (https://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <https://nlg.isi.edu>
# For more information, see README.md
# For license information, see LICENSE

import sys
import os
import os.path as path
import logging


logger = logging.getLogger("pipeline")


METAPHOR_DIR = "{{PIPELINE_CONFIG.METAPHOR_DIR}}"
HENRY_DIR = "{{PIPELINE_CONFIG.HENRY_DIR}}"
BOXER_DIR = "{{PIPELINE_CONFIG.BOXER_DIR}}"
TMP_DIR = "{{PIPELINE_CONFIG.TMP_DIR}}"
GUROBI_HOME = "{{PIPELINE_CONFIG.GUROBI_HOME}}"
GRB_LICENSE_FILE = "{{PIPELINE_CONFIG.GRB_LICENSE_FILE}}"
CPLUS_INCLUDE_PATH = "{{PIPELINE_CONFIG.CPLUS_INCLUDE_PATH}}"
PATH = "{{PIPELINE_CONFIG.PATH}}"
LD_LIBRARY_PATH = "{{PIPELINE_CONFIG.LD_LIBRARY_PATH}}"
LIBRARY_PATH = "{{PIPELINE_CONFIG.LIBRARY_PATH}}"
UPLOADS_DIR = "{{PIPELINE_CONFIG.UPLOADS_DIR}}"

SPANISH_PIPELINE = path.join(
    METAPHOR_DIR,
    "pipelines/Spanish/run-es.sh"
)

FARSI_PIPELINE = path.join(
    METAPHOR_DIR,
    "pipelines/Farsi/run-fa.sh"
)

RUSSIAN_PIPELINE = path.join(
    METAPHOR_DIR,
    "pipelines/Russian/run-ru.sh"
)


BOXER2HENRY = path.join(
    METAPHOR_DIR,
    "pipelines/English/parse-to-lf/Boxer2Henry.py"
)

PARSER2HENRY = path.join(
    METAPHOR_DIR,
    "pipelines/common/IntParser2Henry.py"
)

KBS_DIR = path.join(METAPHOR_DIR, "KBs")

EN_KB_PATH = path.join(KBS_DIR, "English/English_compiled_KB.da")
ES_KB_PATH = path.join(KBS_DIR, "Spanish/Spanish_compiled_KB.da")
RU_KB_PATH = path.join(KBS_DIR, "Russian/Russian_compiled_KB.da")
FA_KB_PATH = path.join(KBS_DIR, "Farsi/Farsi_compiled_KB.da")

CODE_RU = path.join(METAPHOR_DIR, "pipelines/Russian")
CODE_EN = path.join(METAPHOR_DIR, "pipelines/English")
CODE_ES = path.join(METAPHOR_DIR, "pipelines/Spanish")
CODE_FA = path.join(METAPHOR_DIR, "pipelines/Farsi")
CODE_COMMON = path.join(METAPHOR_DIR, "pipelines/common")


sys.path.extend([CODE_RU, CODE_EN, CODE_ES, CODE_FA, CODE_COMMON])


logger.info("METAPHOR_DIR: %r" % os.environ.get("METAPHOR_DIR"))
logger.info("HENRY_DIR: %r" % os.environ.get("HENRY_DIR"))
logger.info("BOXER_DIR: %r" % os.environ.get("BOXER_DIR"))
logger.info("TMP_DIR: %r" % os.environ.get("TMP_DIR"))
logger.info("GUROBI_HOME: %r" % os.environ.get("GUROBI_HOME"))
logger.info("GRB_LICENSE_FILE: %r" % os.environ.get("GRB_LICENSE_FILE"))
logger.info("CPLUS_INCLUDE_PATH: %r" % os.environ.get("CPLUS_INCLUDE_PATH"))
logger.info("PATH: %r" % os.environ.get("PATH"))
logger.info("LD_LIBRARY_PATH: %r" % os.environ.get("LD_LIBRARY_PATH"))
logger.info("LIBRARY_PATH: %r" % os.environ.get("LIBRARY_PATH"))

logger.info("SPANISH_PIPELINE: %s" % SPANISH_PIPELINE)
logger.info("FARSI_PIPELINE: %s" % FARSI_PIPELINE)
logger.info("RUSSIAN_PIPELINE: %s" % RUSSIAN_PIPELINE)
logger.info("PARSER2HENRY: %s" % PARSER2HENRY)

logger.info("EN_KB_PATH: %s" % EN_KB_PATH)
logger.info("ES_KB_PATH: %s" % ES_KB_PATH)
logger.info("FA_KB_PATH: %s" % FA_KB_PATH)
logger.info("RU_KB_PATH: %s" % RU_KB_PATH)

logger.info("CODE_EN: %s" % CODE_EN)
logger.info("CODE_ES: %s" % CODE_ES)
logger.info("CODE_FA: %s" % CODE_FA)
logger.info("CODE_RU: %s" % CODE_RU)

logger.info("CODE_COMMON: %s" % CODE_COMMON)
