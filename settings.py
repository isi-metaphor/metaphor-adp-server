#!/usr/bin/env python
# coding: utf-8

import os


def project_dir(dir_name):
    return os.path.join(os.path.dirname(__file__), "..", dir_name)\
        .replace("\\", "//")


DEBUG = True
TEMPLATE_DEBUG = DEBUG


ADMINS = ()


MANAGERS = ADMINS
DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.sqlite3",
        "NAME":     "local.db",
    }
}

TIME_ZONE = "America/Chicago"
LANGUAGE_CODE = "en-us"

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True


MEDIA_ROOT = project_dir("/static/media/")
MEDIA_URL = "/media/"


STATIC_ROOT = "/static/"
STATIC_URL = "/static/"
STATICFILES_DIRS = (
    project_dir("static"),
)
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

SECRET_KEY = "c=&amp;x^$bt(=4q@jyjuhmc)q_)75znjnddzzx9u9(1sb7hb#%8fc"
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)


ROOT_URLCONF = "lccsrv.urls"
WSGI_APPLICATION = "lccsrv.wsgi.application"

import os
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), "..", "templates").replace("\\","/"),)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
)


LOGGING = {}
