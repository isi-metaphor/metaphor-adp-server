# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

import lz4
import json
import StringIO as stringio

from  datetime import datetime

from django.db import models
from django.http import HttpResponse


class TASK_STATUS:

    DOCUMENT_RECEIVED = 0
    PREPROCESSED      = 1
    PROCESSED         = 2


class AnnotationTask(models.Model):

    class Meta:
        db_table = "t_tasks"

    request_addr        = models.CharField(null=True, blank=True, max_length=16)
    request_time        = models.DateTimeField(auto_now_add=True, null=False)
    request_lang        = models.CharField(max_length=32, null=True)
    request_body_blob   = models.BinaryField(null=False)

    henry_out_blob      = models.BinaryField(null=True)

    response_body_blob  = models.BinaryField(default=None, null=True)
    response_time       = models.DateTimeField(null=True)
    response_status     = models.IntegerField(null=False, default=500)

    task_status         = models.SmallIntegerField(null=False, default=TASK_STATUS.DOCUMENT_RECEIVED)
    task_error_count    = models.IntegerField(default=0, null=False)
    task_log_blob       = models.BinaryField(null=False)
    task_error_message  = models.CharField(max_length=256, null=True, blank=True)
    task_error_code     = models.IntegerField(null=False, default=0)

    def __init__(self, *args, **kwargs):
        super(AnnotationTask, self).__init__(*args, **kwargs)
        self.log = stringio.StringIO()

    def status_str(self):
        if self.task_status == TASK_STATUS.DOCUMENT_RECEIVED:
            return "RECEIVED"
        if self.task_status == TASK_STATUS.PREPROCESSED:
            return "PREPROCESSED"
        if self.task_status == TASK_STATUS.PROCESSED:
            return "PROCESSED"
        return "UNKNOWN"

    def error_code_str(self):
        if self.task_error_code == 0:
            return "OK"
        if self.task_error_code == 1:
            return "SERVER_ERR"
        if self.task_error_code == 3:
            return "NO_LANG_ERR"
        if self.task_error_code == 4:
            return "NO_ANNO_ERR"
        if self.task_error_code == 6:
            return "NO_META_ERR"
        return "UNKNOWN"

    def log_error(self, error_msg):
        self.log.write(error_msg)
        self.log.write("\n")

    def to_response(self, save=True):

        if self.task_error_code != 0:
            if self.response_body_blob is None:
                response_body = self.request_body
                self.response_body = response_body
            else:
                response_body = self.response_body
        else:
            if self.response_body_blob is None:
                response_body = json.dumps({
                    "error_code": self.task_error_code,
                    "error_message": self.task_error_message,
                })
                self.response_body = response_body
            else:
                response_body = self.response_body

        if save:
            log_str = self.log.getvalue()
            self.task_log_blob = lz4.compressHC(log_str)
            self.response_time = datetime.now()
            self.save()

        return HttpResponse(response_body,
                            content_type="application/json",
                            status=self.response_status)

    @property
    def request_body(self):
        return lz4.decompress(self.request_body_blob)

    @request_body.setter
    def request_body(self, value):
        self.request_body_blob = lz4.compressHC(value)

    @property
    def henry_out(self):
        return lz4.decompress(self.henry_out_blob)

    @henry_out.setter
    def henry_out(self, value):
        self.henry_out_blob = lz4.compressHC(value)

    @property
    def log_body(self):
        return lz4.decompress(self.task_log_blob)

    @property
    def response_body(self):
        return lz4.decompress(self.response_body_blob)

    @response_body.setter
    def response_body(self, value):
        self.response_body_blob = lz4.compressHC(value)
