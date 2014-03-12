# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

import logging

from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate


logger = logging.getLogger(__name__)


def app(request):
    if request.method == "POST":
        username = request.POST["user-name"]
        password = request.POST["user-pass"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, "app.html", {
                    "message_level": "info",
                    "message": "You successfully logged in.",
                })
            else:
                logger.info("User: %s. Tried to log-in app. Error: Wrong username/password." % username)
                return render(request, "login.html", {
                    "message": "User is not active.",
                    "message_level": "danger",
                })
        else:
            logger.info("User: %s. Tried to log-in app. Error: Wrong username/password." % username)
            return render(request, "login.html", {
                "message": "Wrong username/password.",
                "message_level": "danger",
            })
    else:
        print request.user
        if request.user.is_anonymous():
            return render(request, "login.html", {})
        else:
            logger.info("User: %s. Accessed app." % request.user.username)
            return render(request, "app.html", {})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/app/")


def run_pipeline(request):

    if request.method == "POST":
        pass
    else:
        return HttpResponse("<b>Error: use POST method to submit query file.</b>",
                            status=405)