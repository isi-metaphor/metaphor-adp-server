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


def dev():
    env.config = {
        "repository":   "https://github.com/isi-metaphor/lcc-service.git",
        "branch":       "dev",
        "context":       json.load(open("fab/config.dev.json", "r")),
    }
    env.config["path"] = env.config["context"]["ROOT"]
    env.config["stage"] = env.config["context"]["STAGE"]


def prod():
    env.config = {
        "repository":   "https://github.com/isi-metaphor/lcc-service.git",
        "branch":       "master",
        "context":      json.load(open("fab/config.prod.json", "r")),
    }
    env.config["path"] = env.config["context"]["ROOT"]
    env.config["stage"] = env.config["context"]["STAGE"]


def run_local():
    env.host_string = "localhost"
    env.user = "zvm"
    env.local = True
    local("pypy manage.py runserver 0.0.0.0:8000 --settings=settings")


def server():
    env.host_string = "colo-vm19.isi.edu"
    env.user = "metaphor"
    env.key_filename = "~/.ssh/id_dsa"
    env.local = False


def init():
    if not env.local:
        run("sudo aptitude -f install %s" % " ".join((
            "git",
            "uwsgi",
            "nginx",
            "python",
            "sqlite3",
            "sqlite3-dev",
            "uwsgi-plugin-python",
        )))
        if not fabric.contrib.files.exists(env.config["path"]):
            run("git clone {repository} -b {branch} {path}".format(**env.config))


def commit():
     local("git add -A")
     local("git diff --quiet --exit-code --cached || git commit -m 'Update'")
     local("git push")
     print(green('Committed and pushed to git.', bold=False))


def update():
    print(green("Updating packages."))
    run("sudo pip install -r requirements.txt")


def deploy():

    env.lcwd = os.path.dirname(__file__)

    config = env.config
    context = config["context"]

    print(red("Beginning Deploy to: {user}@{host_string}".format(**env)))

    with cd("%s/" % env.config["path"]):
        run("pwd")

        print(green("Switching branch."))
        run("git checkout {branch}".format(**config))

        print(green("Pulling from GitHub."))
        run("git pull")

        print(green("Uploading bashrc"))
        bashrcFile="fab/bashrc.sh"
        generateBashConfig(bashrcFile)
        fabric.contrib.files.upload_template(bashrcFile,
                                             "{path}/bashrc.sh".format(**config),
                                             context=context,
                                             use_jinja=True)
        run("cp -f {path}/bashrc.sh ~/metaphor.sh".format(**config))

        print(green("Uploading setting.py"))
        fabric.contrib.files.upload_template("fab/settings.py",
                                             "{path}/lccsrv/settings.py".format(**config),
                                             context=context,
                                             use_jinja=True)
        fabric.contrib.files.upload_template("fab/paths.py",
                                             "{path}/lccsrv/paths.py".format(**config),
                                             context=context,
                                             use_jinja=True)

        print(green("Uploading usgi.ini"))
        fabric.contrib.files.upload_template("fab/uwsgi.ini",
                                             "{path}/uwsgi.ini".format(**config),
                                             context=context,
                                             use_jinja=True)
        run("sudo cp -f {path}/uwsgi.ini /etc/uwsgi/apps-available/{stage}.ini".format(**config))
        run("sudo ln -sf /etc/uwsgi/apps-available/{stage}.ini /etc/uwsgi/apps-enabled/{stage}.ini".format(**config))
        run("sudo /etc/init.d/uwsgi stop {stage}".format(**config))

        print(green("Uploading nginx config"))
        fabric.contrib.files.upload_template("fab/nginx.conf",
                                             "{path}/nginx.conf".format(**config),
                                             context=context,
                                             use_jinja=True)
        run("sudo cp -f {path}/nginx.conf /etc/nginx/sites-available/{stage}".format(**config))
        run("sudo ln -sf /etc/nginx/sites-available/{stage} /etc/nginx/sites-enabled/{stage}".format(**config))
        run("sudo /etc/init.d/nginx stop".format(**config))

        # print(green("Syncing database."))
        # # run("python manage.py syncdb --noinput")

        # print(green("Creating indexes."))
        # run("python manage.py syncdb --noinput --settings=lccsrv.settings")


def test_client():
    port = env.config["context"]["NGINX_PORT"]
    host = env.config["context"]["NGINX_SERVER_NAME"]
    for file_path in glob.glob("testdata/queries/*.json"):
        cmd = "python oldclient/client.py -g %s -p %d -j %s" % (host, port, file_path)
        print(green(cmd))
        run(cmd)


def devdeploy():
    dev()
    server()
    #init()
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


def proddeploy():
    prod()
    server()
    #init()
    deploy()
