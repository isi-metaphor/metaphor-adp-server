#!/usr/bin/env python
# coding: utf-8

import os


def project_dir(dir_name):
    return os.path.join(os.path.dirname(__file__), "..", dir_name)\
        .replace("\\", "//")


DEBUG = {{DJANGO_DEBUG}}
TEMPLATE_DEBUG = DEBUG


ADMINS = (
    ("{{ADMIN_NAME}}", "{{ADMIN_EMAIL}}"),
)


MANAGERS = ADMINS
DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.sqlite3",
        "NAME":     "{{DJANGO_DB_NAME}}",
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


ROOT_URLCONF = "yerba.urls"
WSGI_APPLICATION = "yerba.wsgi.application"

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


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    }
}
