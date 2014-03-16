# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",
                       url(r"^$",                   "pipeline.views.run_pipeline",  name="pipeline"),
                       url(r"^annotateDocument",    "pipeline.views.run_pipeline",  name="pipeline"),
                       url(r"^app/$",               "pipeline.views.app",           name="app"),
                       url(r"^logout/$",            "pipeline.views.user_logout",   name="logout"),
                       url(r"^admin/",              include(admin.site.urls)),
                       )
