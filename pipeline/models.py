# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

import lz4
import StringIO as stringio

from  datetime import datetime

from django.db import models
from django.http import HttpResponse


class TASK_STATUS:

    DOCUMENT_RECEIVED = 0
    PREPROCESSED = 1


class AnnotationTask(models.Model):

    class Meta:
        db_table = "t_tasks"

    request_time = models.DateTimeField(auto_now_add=True, null=False)
    request_lang = models.CharField(max_length=32, null=True)
    request_body_blob = models.BinaryField(null=False)

    response_body_blob = models.BinaryField(default=lz4.compressHC("{'message':'Response not set.'}"), null=True)
    response_time = models.DateTimeField(null=True)
    response_status = models.IntegerField(null=False, default=200)

    task_status = models.SmallIntegerField(null=False, default=TASK_STATUS.DOCUMENT_RECEIVED)
    task_error_count = models.IntegerField(default=0, null=False)
    task_log_blob = models.BinaryField(null=False)
    task_error_message = models.CharField(max_length=256, null=True, blank=True)
    task_error_code = models.IntegerField(null=False, default=0)

    def __init__(self, *args, **kwargs):
        super(AnnotationTask, self).__init__(*args, **kwargs)
        self.log = stringio.StringIO()

    def save(self, *args, **kwargs):
        self.task_log_blob = lz4.compressHC(self.log.getvalue())
        super(AnnotationTask, self).save(*args, **kwargs)

    def log_error(self, error_msg):
        self.log.write(error_msg)
        self.log.write("\n")

    def to_response(self, save=True):

        if save:
            self.response_time = datetime.now()

        return HttpResponse("{}", content_type="application/json")


    @property
    def request_body(self):
        return lz4.decompress(self.request_body_blob)

    @request_body.setter
    def request_body(self, value):
        self.request_body_blob = lz4.compressHC(value)

    @property
    def response_body(self):
        return lz4.decompress(self.response_body_blob)

    @response_body.setter
    def response_body(self, value):
        self.response_body_blob = lz4.compressHC(value)