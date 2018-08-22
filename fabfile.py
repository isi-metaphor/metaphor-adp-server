#!/usr/bin/env python2.7
# coding: utf-8

# Copyright (C) University of Southern California (https://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <https://nlg.isi.edu>
# For more information, see README.md
# For license information, see LICENSE

import os
import json
import fabric

from fabric.api import *
from fabric.colors import green, red


def basic_config(branch):
    env.config = {
        "repository": "https://github.com/isi-metaphor/metaphor-adp-server.git",
        "branch": branch,
        "context": json.load(open("fab/config." + branch + ".json", "r")),
    }
    env.config["path"] = env.config["context"]["ROOT"]
    env.config["stage"] = env.config["context"]["STAGE"]


def local_config():
    env.host_string = "localhost"
    env.user = "metaphor"
    env.local = True


def remote_config():
    env.host_string = "colo-pm4.isi.edu"
    env.user = "metaphor"
    env.key_filename = "~/.ssh/id_dsa"
    env.local = False


def generate_bash_config(file):
    with open(file, "wb") as fo:
        fo.write("export METAPHOR_DIR=" +
                 env.config["context"]["PIPELINE_CONFIG"]["METAPHOR_DIR"] +
                 "\n")
        fo.write("export PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/pipelines/common:$METAPHOR_DIR/pipelines/Russian:$METAPHOR_DIR/pipelines/English:$METAPHOR_DIR/pipelines/Farsi:$METAPHOR_DIR/pipelines/Spanish\n\n")

        fo.write("export HENRY_DIR=" +
                 env.config["context"]["PIPELINE_CONFIG"]["HENRY_DIR"] + "\n")
        fo.write("export BOXER_DIR=" +
                 env.config["context"]["PIPELINE_CONFIG"]["BOXER_DIR"] + "\n")
        fo.write("export TMP_DIR=" +
                 env.config["context"]["PIPELINE_CONFIG"]["TMP_DIR"] + "\n\n")

        fo.write("export GUROBI_HOME=" +
                 env.config["context"]["PIPELINE_CONFIG"]["GUROBI_HOME"] + "\n")
        fo.write("export GRB_LICENSE_FILE=" +
                 env.config["context"]["PIPELINE_CONFIG"]["GRB_LICENSE_FILE"] +
                 "\n\n")

        fo.write("export CPLUS_INCLUDE_PATH=/usr/include/python2.7/:${GUROBI_HOME}/include\n")
        fo.write("export PATH=${PATH}:/usr/sbin:/sbin:/usr/bin:${GUROBI_HOME}/bin:${JAVA_HOME}/bin\n")
        fo.write("export LD_LIBRARY_PATH=:${GUROBI_HOME}/lib/:${LD_LIBRARY_PATH}\n")
        fo.write("export LIBRARY_PATH=${GUROBI_HOME}/lib\n")
        fo.write("export EMAILS=\"" + env.config["context"]["ADMIN_EMAIL"] +
                 " " + env.config["context"]["OTHER_EMAILS"]+"\"\n")


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
        bashrc_file = "fab/bashrc.sh"
        generate_bash_config(bashrc_file)
        fabric.contrib.files.upload_template(
            bashrc_file,
            "{path}/bashrc.sh".format(**config),
            context=context,
            use_jinja=True)

        print(green("Uploading setting.py"))
        fabric.contrib.files.upload_template(
            "fab/settings.py",
            "{path}/adpsrv/settings.py".format(**config),
            context=context,
            use_jinja=True)
        fabric.contrib.files.upload_template(
            "fab/paths.py",
            "{path}/adpsrv/paths.py".format(**config),
            context=context,
            use_jinja=True)
        fabric.contrib.files.upload_template(
            "fab/temp_run.sh",
            "{path}/temp_run.sh".format(**config),
            context=context,
            use_jinja=True)
        fabric.contrib.files.upload_template(
            "fab/run.sh",
            "{path}/run.sh".format(**config),
            context=context,
            use_jinja=True)
        fabric.contrib.files.upload_template(
            "fab/shell.sh",
            "{path}/shell.sh".format(**config),
            context=context,
            use_jinja=True)
        fabric.contrib.files.upload_template(
            "fab/check_service.sh",
            "{path}/check_service.sh".format(**config),
            context=context,
            use_jinja=True)

        # print(green("Syncing database."))
        # run("python manage.py syncdb --noinput")

        # print(green("Creating indexes."))
        # run("python manage.py syncdb --noinput --settings=adpsrv.settings")


def install(branch):
    basic_config(branch)
    local_config()
    deploy()
