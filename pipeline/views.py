# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

import git
import base64
import logging
import traceback

from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate

from django.views.decorators.csrf import csrf_exempt

from lccsrv import paths
from lccsrv import settings

from pipeline.models import AnnotationTask
from pipeline.annotator import Annotator


logger = logging.getLogger("pipeline")

def app(request):
    if request.method == "POST":
        username = request.POST["user-name"]
        password = request.POST["user-pass"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("/app/status/")
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
        if request.user.is_anonymous():
            return render(request, "login.html", {})
        else:
            logger.info("User: %s. Accessed app." % request.user.username)
            return redirect("/app/status/")


def app_status(request):
    repo = git.Repo(".")
    return render(request, "app_status.html", {
        "branch":   repo.active_branch.name,
        "commit":   base64.b64encode(repo.active_branch.commit.binsha),
        "settings": settings,
        "paths":    paths,
    })



def user_logout(request):
    logout(request)
    logger.info("User: %r. Logged out." % request.user)
    return HttpResponseRedirect("/app/")


@csrf_exempt
def run_pipeline(request):

    if request.method == "POST":

        try:
            task = AnnotationTask()
            task.request_body = request.body
            task.save()
            logger.info("Task created. Id=%d." % task.id)
        except Exception:
            msg = "Cannot create tack."
            logger.error(msg + " Traceback: %s" % traceback.format_exc())
            return HttpResponse(msg, status=500)

        try:
            pipeline = Annotator(logger, task)
            logger.info("Pipeline initialized")
        except Exception:
            msg = "Cannot initialize pipeline."
            logger.error(msg + " Traceback: %s" % traceback.format_exc())
            return HttpResponse(msg, status=500)

        try:
            pipeline.annotate()
        except Exception:
            msg = "Error while annotating document. Traceback:\n%s." % traceback.format_exc()
            logger.error(msg)
            try:
                task.log_error(msg)
            except Exception:
                logger.error("Error while saving failed task. Traceback: %s" % traceback.format_exc())

        try:
            response = task.to_response(save=True)
            return response
        except Exception:
            logger.error("Error while saving failed task. Traceback: %s" % traceback.format_exc())

        return HttpResponse("", status=500)

    else:
        return HttpResponse("<b>Error: use POST method to submit query file.</b>",
                            status=405)