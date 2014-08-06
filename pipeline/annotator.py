# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

import os
import simplejson as json
import pipeline.external as adb
import subprocess
import tempfile
from lccsrv import paths
from pipeline.models import TASK_STATUS


class Annotator(object):

    def __init__(self, logger, task):
        self.logger = logger
        self.task = task

    def task_error(self, error_msg, error_code=None, count_error=False):
        self.logger.error(error_msg)
        self.task.log_error(error_msg)
        self.task.task_error_message = error_msg
        if error_code is not None:
            self.task.task_error_code = error_code
        if count_error:
            self.task.task_error_count += 1
        return self.task

    def normalize(self,string,language):
        if language == "EN":
            # Replacing single quote, double quote (start/end), dash
            ascii_metaphor = string.replace(u"\u2019", u"\u0027")\
                .replace(u"\u201c", u"\u0022")\
                .replace(u"\u201d", u"\u0022")\
                .replace(u"\u2014", u"\u002d")
            return ascii_metaphor
        else:
            return string

    def annotate(self):

        # 1.
        log_msg = "Start annotating document."
        self.logger.info(log_msg)
        self.task.log_error(log_msg)
        metaphors = {}
        sourcePhrases={}
        targetPhrases={}
        request_document_body = self.task.request_body


        # 2. Parse document JSON
        log_msg = "Parse document json. Task id=%d, document size=%d.." % (self.task.id, len(request_document_body))
        self.logger.info(log_msg)
        self.task.log_error(log_msg)
        request_document = json.loads(request_document_body)

        # 2.1 Get last processing step
        last_step = request_document.get("step", 3)
        log_msg = "Last processing step will be %r" % last_step
        self.logger.info(log_msg)
        self.task.log_error(log_msg)
        if last_step not in (1, 2, 3):
            log_msg = "Wrong last step value: %r" % last_step
            self.logger.info(log_msg)
            self.task.log_error(log_msg)
            last_step = 3

        # 2.2 Get selected KB
        selected_kb = request_document.get("kb", None)
        log_msg = "Selected KB is '%r'" % selected_kb
        self.logger.info(log_msg)
        self.task.log_error(log_msg)
        if selected_kb is not None:
            # Default KB
            if "/" in selected_kb:
                selected_kb = os.path.join(paths.METAPHOR_DIR, selected_kb)
            else:
                selected_kb = os.path.join(paths.UPLOADS_DIR, selected_kb)
            log_msg = "Selected KB full path is '%r'" % selected_kb
            self.logger.info(log_msg)
            self.task.log_error(log_msg)
        # 2.2.1 Get kb content if supplied
        kb_content = request_document.get("kb_content", None)
        inputHandleAndName=None
        outputHandleAndName=None
        if kb_content is not None:
            log_msg = "KB content is NON NULL. overwriting selected_kb"
            self.logger.info(log_msg)
            self.task.log_error(log_msg)
            inputHandleAndName=tempfile.mkstemp(dir=paths.UPLOADS_DIR)
            outputHandleAndName=tempfile.mkstemp(dir=paths.UPLOADS_DIR)
            f = os.fdopen(inputHandleAndName[0], "w")
            f.write(kb_content)
            f.close()
            subprocess.check_call([paths.HENRY_DIR+"/bin/henry", "-m", "compile_kb",inputHandleAndName[1],"-o",outputHandleAndName[1]])
            selected_kb = outputHandleAndName[1]
            log_msg = "Selected KB full path is '%r'" % selected_kb
            self.logger.info(log_msg)
            self.task.log_error(log_msg)

        # 2.3 Get debug option
        debug_option = request_document.get("enableDebug", False)

        # 3. Get document language.
        log_msg = "Getting document language. Task id=%d." % self.task.id
        self.logger.info(log_msg)
        self.task.log_error(log_msg)
        try:
            language = request_document["language"]
        except KeyError:
            error_msg = "No language information available. Task id=%d." % self.task.id
            return self.task_error(error_msg, 3)
        self.task.request_lang = language

        # 4. Get annotation records.
        self.logger.info("Getting document annotations. Task id=%d." % self.task.id)
        try:
            annotations = request_document["metaphorAnnotationRecords"]
        except KeyError:
            error_msg = "No annotations available. Task id=%d." % self.task.id
            return self.task_error(error_msg, 4)

        # 5. Extract annotations.
        self.logger.info("Extracting metaphor entries from document. Task id=%d." % self.task.id)
        annotation_id_index = 0

        for annotation_no, annotation in enumerate(annotations):
            self.logger.info("Extracting annotation #%d." % annotation_no)

            # 5.1 Extracting annotation ID.
            try:
                annotation_id = annotation["sentenceId"]
            except KeyError:
                error_msg = "Ann #%d. No annotation id available (sentenceId). Task=%d" % (
                    annotation_no,
                    self.task.id,
                )
                self.task_error(error_msg, error_code=None, count_error=True)
                annotation_id_index += 1
                annotation_id = annotation_id_index
                
            # 5.2
            try:
                metaphor = annotation["linguisticMetaphor"]
                metaphors[str(annotation_id)]=self.normalize(metaphor,language).encode("utf-8")

            except KeyError:
                error_msg = "Ann #%d. No metaphor available (skip it). Task=%d" % (
                    annotation_no,
                    self.task.id,
                )
                self.task_error(error_msg, error_code=None, count_error=True)
            if "annotationMappings" in annotation:
                ams=annotation["annotationMappings"]
                am=None
                if ams and len(ams)>0:
                    am=ams[0]
                if am and "source" in am:
                    sourcePhrases[str(annotation_id)]=self.normalize(am["source"],language).encode("utf-8")
                if am and "target" in am:
                    targetPhrases[str(annotation_id)]=self.normalize(am["target"],language).encode("utf-8")

        self.logger.info("Task %d language=%s" % (self.task.id, language))
        self.task.language = language
        self.task.task_status = TASK_STATUS.PREPROCESSED
        self.task.response_status = 200

        # 6. If there are no metaphors for annotation, return error.
        if len(metaphors) == 0:
            error_msg = "Found 0 metaphors for annotation. Task id=#%d."
            return self.task_error(error_msg, 6)

        # 7 Get henry max depth
        depth = request_document.get("depth",'3')
        log_msg = "Selected HENRY max depth is '%s'" % depth
        self.logger.info(log_msg)
        self.task.log_error(log_msg)

        # 8 generate graph (even if no debug option)
        dograph = request_document.get("dograph",False) or debug_option
        log_msg = "dograph is {0} {1}".format(dograph ,debug_option)
        self.logger.info(log_msg)
        self.task.log_error(log_msg)

        # 9 select which extractor code to run
        extractor = request_document.get("extractor","extractor-no-span-june-2014-eval")
        log_msg = "using this extractor code: legacy/{0}.py".format(extractor)
        self.logger.info(log_msg)
        self.task.log_error(log_msg)

	# 10 include parser and henry processing times
	parser_time = request_document.get("parser_time", "Absent")
	if parser_time != "Absent":
		request_document["parser_time"] = ""
	henry_time = request_document.get("henry_time", "Absent")
	if henry_time != "Absent":
		request_document["henry_time"] = ""
	# 11 used to indicate whether to use the input metaphor or just the parser output
	parser_output = request_document.get("parser_output", "Absent")
	if parser_output != "Absent":
		request_document["parser_output"] = parser_output 
        result = adb.run_annotation(request_document,
                                    metaphors,
                                    language,
                                    self.task,
                                    self.logger,
                                    with_pdf_content=dograph,
                                    last_step=last_step,
                                    kb=selected_kb,
                                    depth=depth,
                                    extractor=extractor,
                                    sources=sourcePhrases,
                                    targets=targetPhrases)
        if inputHandleAndName is not None:
            os.unlink(inputHandleAndName[1])
        if outputHandleAndName is not None:
            os.unlink(outputHandleAndName[1])

        self.task.response_body = result
        self.task.task_status = TASK_STATUS.PROCESSED

        return debug_option
