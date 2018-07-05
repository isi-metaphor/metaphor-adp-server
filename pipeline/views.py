# coding: utf-8

# Copyright (C) University of Southern California (https://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <https://nlg.isi.edu>
# For more information, see README.md
# For license information, see LICENSE

import os
import git
import glob
import json
import logging
import traceback

from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger

from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate

from django.views.decorators.csrf import csrf_exempt

from lccsrv import paths
from lccsrv import settings

from pipeline.models import AnnotationTask, LogsDisplay
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
    if request.user.is_anonymous():
        return redirect("/app/")
    repo = git.Repo(".")
    return render(request, "app_status.html", {
        "branch": repo.git.execute(["git", "describe", "--all",
                                    "--exact-match", str(repo.head.commit)]),
        "commit": str(repo.head.commit),
        "settings": settings,
        "paths": paths
    })


def app_logs(request):
    if request.user.is_anonymous():
        return redirect("/app/")

    page_size = 30
    page_num = request.GET.get("page", "1")
    items = LogsDisplay.objects.order_by("-request_time")
    pages = Paginator(items, page_size)

    try:
        page = pages.page(page_num)
    except PageNotAnInteger:
        page = pages.page(1)
    except EmptyPage:
        page = pages.page(pages.num_pages)

    return render(request, "app_logs.html", {
        "page": page,
        "page_range": xrange(max(1, page.number - 7),
                             min(pages.num_pages + 1, page.number + 7)),
    })


def app_item(request):
    if request.user.is_anonymous():
        return redirect("/app/")
    try:
        item = AnnotationTask.objects.get(id=request.GET.get("id"))
    except:
        item = None
    return render(request, "app_item.html", {
        "item": item,
    })


def app_request(request):
    if request.user.is_anonymous():
        return redirect("/app/")
    return render(request, "app_request.html", {

    })


def app_list_kbs(request):
    default_kbs = glob.glob(paths.KBS_DIR + "/*/*.da")
    default_kbs = [
        paths.EN_KBPATH,
        paths.RU_KBPATH,
        paths.ES_KBPATH,
        paths.FA_KBPATH,
    ]
    default_kbs = [
        os.path.join(
            os.path.relpath(os.path.basename(os.path.dirname(f))),
            os.path.basename(f)
        )
        for f in default_kbs]

    uploaded_kbs = [
        os.path.basename(f)
        for f in glob.glob(paths.UPLOADS_DIR + "/*.da")
    ]

    return HttpResponse(json.dumps({
        "kbs_dir": paths.KBS_DIR,
        "uploads_dir": paths.UPLOADS_DIR,
        "default_kbs": default_kbs,
        "uploaded_kbs": uploaded_kbs,
    }), content_type="application/json")


def user_logout(request):
    logout(request)
    logger.info("User: %r. Logged out." % request.user)
    return HttpResponseRedirect("/app/")


@csrf_exempt
def run_pipeline(request):
    if request.method == "POST":
        last_msg = ""
        try:
            task = AnnotationTask(request_addr=request.META.get("REMOTE_ADDR"))
            task.request_body = request.body
            task.save()
            logger.info("Task created. Id=%d." % task.id)
        except Exception:
            msg = "Cannot create task. Traceback: %s" % traceback.format_exc()
            last_msg = msg
            logger.error(msg)
            return HttpResponse(msg, status=500)

        try:
            pipeline = Annotator(logger, task)
            logger.info("Pipeline initialized")
        except Exception:
            msg = "Cannot initialize pipeline. Traceback: %s" \
                  % traceback.format_exc()
            last_msg = msg
            logger.error(msg)
            return HttpResponse(msg, status=500)

        try:
            debug_option = pipeline.annotate()
        except Exception:
            debug_option = False
            msg = "Error while annotating document. Traceback:\n%s." \
                  % traceback.format_exc()
            last_msg = msg
            logger.error(msg)
            try:
                task.log_error(msg)
            except Exception:
                msg = "Error 1 while saving failed task. Traceback: %s" % traceback.format_exc()
                last_msg = msg
                logger.error(msg)

        try:
            response = task.to_response(save=True, enable_debug=debug_option)
            logsDisplay = LogsDisplay()
            logsDisplay.fill_table(task)

            return response
        except Exception:
            msg = "Error 2 while saving failed task. Traceback: %s" \
                  % traceback.format_exc()
            last_msg = msg
            logger.error(msg)

        return HttpResponse(last_msg, status=500)

    else:
        return HttpResponse("<b>Error: use POST method to submit query file.</b>",
                            status=405)


@csrf_exempt
def app_upload(request):
    try:
        if request.method == "POST" and request.is_ajax():
            for uploaded in request.FILES.values():
                file_name = os.path.join(paths.UPLOADS_DIR, uploaded.name)
                kb_name = uploaded.name
                with open(file_name, "wb") as fl:
                    fl.write(uploaded.read())
                return HttpResponse(json.dumps({
                    "error_code": 0,
                    "file_name": file_name,
                    "kb_name": kb_name
                }))

        else:
            return HttpResponse(json.dumps({
                "error_code": 2,
                "error_msg": "This is not POST"
            }))
    except:
        traceback.print_exc()
        return HttpResponse(json.dumps({
            "error_code": 1,
            "error_msg": traceback.format_exc()
        }))
