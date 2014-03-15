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


os.environ["METAPHOR_DIR"]          =   METAPHOR_DIR
os.environ["HENRY_DIR"]             =   HENRY_DIR
os.environ["BOXER_DIR"]             =   BOXER_DIR
os.environ["TMP_DIR"]               =   TMP_DIR
os.environ["GUROBI_HOME"]           =   GUROBI_HOME
os.environ["GRB_LICENSE_FILE"]      =   GRB_LICENSE_FILE
os.environ["CPLUS_INCLUDE_PATH"]    =   CPLUS_INCLUDE_PATH
os.environ["PATH"]                  =   PATH
os.environ["LD_LIBRARY_PATH"]       =   LD_LIBRARY_PATH
os.environ["LIBRARY_PATH"]          =   LIBRARY_PATH

os.environ["PYTHONPATH"]            =   "%s:%s:%s:%s:%s:$PYTHONPATH" % (
    CODE_RU,
    CODE_EN,
    CODE_ES,
    CODE_FA,
    CODE_COMMON,
)

sys.path.extend([CODE_RU, CODE_EN, CODE_ES, CODE_FA, CODE_COMMON])


logger.info("Envieronment variables: %s." % "\n".join(os.environ))
