#!/usr/bin/env python
# coding: utf-8

import os
import json
import fabric

from fabric.api import *
from fabric.colors import green, red


def dev():
    env.config = {
        "repository":   "https://github.com/zaycev/lcc-service.git",
        "branch":       "dev",
        "context":       json.load(open("fab/config.dev.json", "r")),
    }
    env.config["path"] = env.config["context"]["ROOT"]
    env.config["stage"] = env.config["context"]["STAGE"]


def prod():
    env.config = {
        "repository":   "https://github.com/zaycev/lcc-service.git",
        "branch":       "prod",
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
    env.user = "vzaytsev"
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
        )))
        if not fabric.contrib.files.exists(env.config["path"]):
            run("git clone {repository} -b {branch} {path}".format(**env.config))


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

        print(green("Uploading setting.py"))
        fabric.contrib.files.upload_template("fab/settings.py",
                                             "{path}/lccsrv/settings.py".format(**config),
                                             context=context,
                                             use_jinja=True)

        print(green("Uploading usgi.ini"))
        fabric.contrib.files.upload_template("fab/uwsgi.ini",
                                             "{path}/uwsgi.ini".format(**config),
                                             context=context,
                                             use_jinja=True)
        run("sudo cp -f {path}/uwsgi.ini /etc/uwsgi/apps-available/{stage}.ini".format(**config))
        run("sudo ln -sf /etc/uwsgi/apps-available/{stage}.ini /etc/uwsgi/apps-enabled/{stage}.ini".format(**config))
        run("sudo /etc/init.d/uwsgi restart {stage}".format(**config))

        print(green("Uploading nginx config"))
        fabric.contrib.files.upload_template("fab/nginx.conf",
                                             "{path}/nginx.conf".format(**config),
                                             context=context,
                                             use_jinja=True)
        run("sudo cp -f {path}/nginx.conf /etc/nginx/sites-available/{stage}".format(**config))
        run("sudo ln -sf /etc/nginx/sites-available/{stage} /etc/nginx/sites-enabled/{stage}".format(**config))
        run("sudo /etc/init.d/nginx restart".format(**config))

        print(green("Syncing database."))
        # run("python manage.py syncdb --noinput")

        print(green("Creating indexes."))
        # run("python manage.py syncdb --noinput")


def devdeploy():
    dev()
    server()
    deploy()


def proddeploy():
    prod()
    server()
    deploy()