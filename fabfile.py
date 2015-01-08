#!/usr/bin/env python
# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE


import os
import json
import glob
import fabric

from fabric.api import *
from fabric.colors import green, red


def basicConfig(branch):
    env.config = {
        "repository":   "https://github.com/isi-metaphor/lcc-service.git",
        "branch":       branch,
        "context":       json.load(open("fab/config."+branch+".json", "r")),
    }
    env.config["path"] = env.config["context"]["ROOT"]
    env.config["stage"] = env.config["context"]["STAGE"]

def localConfig():
    env.host_string = "localhost"
    env.user = "metaphor"
    env.local = True

def remoteConfig():
    env.host_string = "colo-pm4.isi.edu"
    env.user = "metaphor"
    env.key_filename = "~/.ssh/id_dsa"
    env.local = False

def deploy():

    if not fabric.contrib.files.exists(env.config["path"]):
        run("git clone {repository} -b {branch} {path}".format(**env.config))
    env.lcwd = os.path.dirname(__file__)

    config = env.config
    context = config["context"]

    print(red("Beginning Deploy to: {user}@{host_string}".format(**env)))

    with cd("%s/" % env.config["path"]):
        run("pwd")

        print(green("Switching branch."))
        run("git checkout {branch}".format(**config))

        print(green("Uploading bashrc"))
        bashrcFile="fab/bashrc.sh"
        generateBashConfig(bashrcFile)
        fabric.contrib.files.upload_template(bashrcFile,
                                             "{path}/bashrc.sh".format(**config),
                                             context=context,
                                             use_jinja=True)

        print(green("Uploading setting.py"))
        fabric.contrib.files.upload_template("fab/settings.py",
                                             "{path}/lccsrv/settings.py".format(**config),
                                             context=context,
                                             use_jinja=True)
        fabric.contrib.files.upload_template("fab/paths.py",
                                             "{path}/lccsrv/paths.py".format(**config),
                                             context=context,
                                             use_jinja=True)
        fabric.contrib.files.upload_template("fab/tempRun.sh",
                                             "{path}/tempRun.sh".format(**config),
                                             context=context,
                                             use_jinja=True)
        fabric.contrib.files.upload_template("fab/run.sh",
                                             "{path}/run.sh".format(**config),
                                             context=context,
                                             use_jinja=True)
        fabric.contrib.files.upload_template("fab/shell.sh",
                                             "{path}/shell.sh".format(**config),
                                             context=context,
                                             use_jinja=True)
        fabric.contrib.files.upload_template("fab/checkService.sh",
                                             "{path}/checkService.sh".format(**config),
                                             context=context,
                                             use_jinja=True)

        # print(green("Syncing database."))
        # # run("python manage.py syncdb --noinput")

        # print(green("Creating indexes."))
        # run("python manage.py syncdb --noinput --settings=lccsrv.settings")

def install(branch):
    basicConfig(branch)
    localConfig()
    deploy()

def generateBashConfig(file):
    fo = open(file, "wb")
    fo.write("export METAPHOR_DIR="+env.config["context"]["PIPELINE_CONFIG"]["METAPHOR_DIR"]+"\n");
    fo.write("export PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/pipelines/common:$METAPHOR_DIR/pipelines/Russian:$METAPHOR_DIR/pipelines/English:$METAPHOR_DIR/pipelines/Farsi:$METAPHOR_DIR/pipelines/Spanish\n\n")

    fo.write("export HENRY_DIR="+env.config["context"]["PIPELINE_CONFIG"]["HENRY_DIR"]+"\n")
    fo.write("export BOXER_DIR="+env.config["context"]["PIPELINE_CONFIG"]["BOXER_DIR"]+"\n")
    fo.write("export TMP_DIR="+env.config["context"]["PIPELINE_CONFIG"]["TMP_DIR"]+"\n\n")

    fo.write("export GUROBI_HOME="+env.config["context"]["PIPELINE_CONFIG"]["GUROBI_HOME"]+"\n")
    fo.write("export GRB_LICENSE_FILE="+env.config["context"]["PIPELINE_CONFIG"]["GRB_LICENSE_FILE"]+"\n\n")

    fo.write("export CPLUS_INCLUDE_PATH=/usr/include/python2.7/:${GUROBI_HOME}/include\n")
    fo.write("export PATH=${PATH}:/usr/sbin:/sbin:/usr/bin:${GUROBI_HOME}/bin:${JAVA_HOME}/bin\n")
    fo.write("export LD_LIBRARY_PATH=:${GUROBI_HOME}/lib/:${LD_LIBRARY_PATH}\n")
    fo.write("export LIBRARY_PATH=${GUROBI_HOME}/lib\n")
    fo.close()

