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


METAPHOR_DIR = "/research/repo/metaphor"
HENRY_DIR = "/research/repo/henry"
BOXER_DIR = "/research/ext/boxer"
TMP_DIR = "/research/temp"
GUROBI_HOME = "/research/ext/gurobi/linux64"
GRB_LICENSE_FILE = "/research/ext/gurobi/license/gurobi.lic"
CPLUS_INCLUDE_PATH = "/usr/include/python2.7:/research/ext/gurobi/linux64/include"
PATH = "/bin:/sbin:/usr/bin:/usr/sbin:/research/ext/gurboi/linux64/bin"
LD_LIBRARY_PATH = "/research/ext/gurobi/linux64/lib:${LD_LIBRARY_PATH}"
LIBRARY_PATH = "/research/ext/gurobi/linux64/lib:${LIBRARY_PATH}"
UPLOADS_DIR = "/research/temp/uploads"

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

EN_KBPATH = path.join(KBS_DIR, "English/English_compiled_KB.da")
ES_KBPATH = path.join(KBS_DIR, "Spanish/Spanish_compiled_KB.da")
RU_KBPATH = path.join(KBS_DIR, "Russian/Russian_compiled_KB.da")
FA_KBPATH = path.join(KBS_DIR, "Farsi/Farsi_compiled_KB.da")

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

logger.info("EN_KBPATH: %s" % EN_KBPATH)
logger.info("ES_KBPATH: %s" % ES_KBPATH)
logger.info("FA_KBPATH: %s" % FA_KBPATH)
logger.info("RU_KBPATH: %s" % RU_KBPATH)

logger.info("CODE_EN: %s" % CODE_EN)
logger.info("CODE_ES: %s" % CODE_ES)
logger.info("CODE_FA: %s" % CODE_FA)
logger.info("CODE_RU: %s" % CODE_RU)

logger.info("CODE_COMMON: %s" % CODE_COMMON)
