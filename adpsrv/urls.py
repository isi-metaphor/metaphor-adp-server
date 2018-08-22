# coding: utf-8

# Copyright (C) University of Southern California (https://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <https://nlg.isi.edu>
# For more information, see README.md
# For license information, see LICENSE

from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    "",
    url(r"^$", "pipeline.views.run_pipeline", name="pipeline"),
    url(r"^annotateDocument", "pipeline.views.run_pipeline", name="pipeline"),
    url(r"^app/$", "pipeline.views.app", name="app"),
    url(r"^app/status/$", "pipeline.views.app_status", name="app_status"),
    url(r"^app/logs/$", "pipeline.views.app_logs", name="app_logs"),
    url(r"^app/item/$", "pipeline.views.app_item", name="app_item"),
    url(r"^app/request/$", "pipeline.views.app_request", name="app_request"),
    url(r"^app/list_kbs/$", "pipeline.views.app_list_kbs", name="list_kbs"),
    url(r"^app/upload/$", "pipeline.views.app_upload", name="upload"),
    url(r"^logout/$", "pipeline.views.user_logout", name="logout"),
    url(r"^admin/", include(admin.site.urls)),
)
