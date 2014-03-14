# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

import os

METAPHOR_DIR        =  "{{METAPHOR_DIR}}"
HENRY_DIR           =  "{{HENRY_DIR}}"
BOXER_DIR           =  "{{BOXER_DIR}}"
TMP_DIR             =  "{{TMP_DIR}}"
GUROBI_HOME         =  "{{GUROBI_HOME}}"
GRB_LICENSE_FILE    =  "{{GRB_LICENSE_FILE}}"

FARSI_PIPELINE      =  os.path.join(METAPHOR_DIR, "/pipelines/Farsi/LF_Pipeline")
SPANISH_PIPELINE    =  os.path.join(METAPHOR_DIR, "/pipelines/Spanish/run_spanish.sh")
RUSSIAN_PIPELINE    =  os.path.join(METAPHOR_DIR, "/pipelines/Russian/run_russian.sh")

BOXER2HENRY         =   os.path.join(METAPHOR_DIR, "/pipelines/English/Boxer2Henry.py")
PARSER2HENRY        =   os.path.join(METAPHOR_DIR, "/pipelines/common/IntParser2Henry.py")

EN_KBPATH           =   os.path.join(METAPHOR_DIR, "/KBs/English/English_compiled_KB.da")
ES_KBPATH           =   os.path.join(METAPHOR_DIR, "/KBs/Spanish/Spanish_compiled_KB.da")
RU_KBPATH           =   os.path.join(METAPHOR_DIR, "/KBs/Russian/Russian_compiled_KB.da")
FA_KBPATH           =   os.path.join(METAPHOR_DIR, "/KBs/Farsi/Farsi_compiled_KB.da")

os.environ["METAPHOR_DIR"]      =   METAPHOR_DIR
os.environ["HENRY_DIR"]         =   HENRY_DIR
os.environ["BOXER_DIR"]         =   BOXER_DIR
os.environ["TMP_DIR"]           =   TMP_DIR
os.environ["GUROBI_HOME"]       =   GUROBI_HOME
os.environ["GRB_LICENSE_FILE"]  =   GRB_LICENSE_FILE