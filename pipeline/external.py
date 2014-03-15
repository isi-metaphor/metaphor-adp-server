# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

import os
import time
import traceback

from lccsrv.paths import *
from legacy.extractor import *
from subprocess import Popen, PIPE
from StringIO import StringIO

ENV = os.environ

kbcompiled = True

DESCRIPTION = "Abductive engine output; "                                                           \
              "targetFrame: Is currently equal to targetConceptSubDomain;"                          \
              "targetConceptDomain: Target concept domain defined by abduction; "                   \
              "targetConceptSubDomain: Target concept subdomain defined by abduction ; "            \
              "sourceFrame: Source frame proposed by abduction ; "                                  \
              "sourceConceptSubDomain: Source subdomain proposed by abduction ; "                   \
              "targetFrameElementSentence: List of words denoting the target found by abduction; "  \
              "sourceFrameElementSentence: List of words denoting the source found by abduction; "  \
              "annotationMappings: Target-Source mapping structures. "                              \
              "isiAbductiveExplanation: Target-Source mapping (metaphor interpretation) as "        \
              "logical form found by abduction."


def extract_parses(input_string):
    output_dict = dict()
    pattern = re.compile('.+\(\s*name\s+([^\)]+)\)')
    for line in input_string.splitlines():
        match_obj = pattern.match(line)
        if match_obj:
            target = match_obj.group(1)
            output_dict[target] = line
    return output_dict


def extract_hypotheses(input_string):
    output_dict = dict()
    hypothesis_found = False
    target_pattern = re.compile('<result-inference target="(.+)"')
    target_string = ""
    for line in input_string.splitlines():
        match_obj = target_pattern.match(line)
        if match_obj:
            target_string = match_obj.group(1)
        elif line.startswith("<hypothesis"):
            hypothesis_found = True
        elif line.startswith("</hypothesis>"):
            hypothesis_found = False
        elif hypothesis_found:
            output_dict[target_string] = line
            target_string = ""
            hypothesis_found = False
    return output_dict


def generate_text_input(input_metaphors, language):
    output_str = ""
    for key in input_metaphors.keys():
        output_str += "<META>" + key + "\n\n " + input_metaphors[key] + "\n\n"

    return output_str


# withPDFContent=true; generate graphs and include PDF content
# as base-64 in output

def run_annotation(request_body_dict, input_metaphors, language, task, logger, with_pdf_content):
    start_time = time.time()
    input_str = generate_text_input(input_metaphors, language)

    # Parser pipeline
    parser_proc = ""
    if language == "FA":
        parser_proc = FARSI_PIPELINE + " | python " + PARSER2HENRY + " --nonmerge sameid freqpred"
        KBPATH = FA_KBPATH

    elif language == "ES":
        parser_proc = SPANISH_PIPELINE + " | python " + PARSER2HENRY + " --nonmerge sameid freqpred"
        KBPATH = ES_KBPATH

    elif language == "RU":
        parser_proc = RUSSIAN_PIPELINE + " | python " + PARSER2HENRY + " --nonmerge sameid freqpred"
        KBPATH = RU_KBPATH

    elif language == "EN":
        tokenizer = BOXER_DIR + "/bin/tokkie --stdin"
        candcParser = BOXER_DIR + "/bin/candc --models " + BOXER_DIR + "/models/boxer --candc-printer boxer"
        boxer = BOXER_DIR + "/bin/boxer --semantics tacitus --resolve true --stdin"
        b2h = "python " + BOXER2HENRY + " --nonmerge sameid freqpred"
        parser_proc = tokenizer + " | " + candcParser + " | " + boxer + " | " + b2h
        KBPATH = EN_KBPATH

    logger.info("Running parsing command: '%s'." % parser_proc)
    logger.info("Input str: %r" % input_str)

    parser_pipeline = Popen(parser_proc,
                            env=ENV,
                            shell=True,
                            stdin=PIPE,
                            stdout=PIPE,
                            stderr=None,
                            close_fds=True)
    parser_output, parser_stderr = parser_pipeline.communicate(input=input_str)

    # Parser processing time in seconds
    parser_time = (time.time() - start_time) * 0.001
    logger.info("Command finished. Processing time: %r." % parser_time)
    logger.info("Command STDERR:\n %r" % parser_stderr)

    # time to generate final output in seconds
    generate_output_time = 2

    # time left for Henry in seconds
    time_all_henry = 600 - parser_time - generate_output_time

    if with_pdf_content:
        # time for graph generation subtracted from Henry time in seconds
        time_all_henry -= - 3

    # time for one interpretation in Henry in seconds
    time_unit_henry = str(int(time_all_henry / len(input_metaphors)))

    # Henry processing
    if kbcompiled:
        henry_proc = HENRY_DIR + "/bin/henry -m infer -e " + HENRY_DIR + \
                     "/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T " + \
                     time_unit_henry + " -b " + KBPATH
    else:
        henry_proc = HENRY_DIR + "/bin/henry -m infer -e " + HENRY_DIR + \
                     "/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T " + \
                     time_unit_henry

    logger.info("Running Henry command: '%s'." % henry_proc)
    henry_pipeline = Popen(henry_proc,
                           env=ENV,
                           shell=True,
                           stdin=PIPE,
                           stdout=PIPE,
                           stderr=None,
                           close_fds=True)
    henry_output, henry_stderr = henry_pipeline.communicate(input=parser_output)
    hypotheses = extract_hypotheses(henry_output)
    logger.info("Parsing Henry output. %r" % parser_output)
    logger.info("Henry STDERR:\n %r" % henry_stderr)

    parses = extract_parses(parser_output)
    processed, failed, empty = 0, 0, 0

    # merge ADB result and input json document
    input_annotations = request_body_dict["metaphorAnnotationRecords"]

    total = len(input_annotations)
    hkeys = hypotheses.keys()
    for annotation in input_annotations:
        if "sentenceId" in annotation:
            sID = str(annotation["sentenceId"])
            if sID in hkeys:
                CM_output = extract_CM_mapping(sID, hypotheses[sID], parses[sID], DESCRIPTION, annotation)
                try:
                    for annot_property in CM_output.keys():
                        if CM_output.get(annot_property):
                            annotation[annot_property] = CM_output[annot_property]
                    processed += 1
                    logger.info("Processed sentence #%s." % sID)

                except Exception:
                    failed += 1
                    error_msg = "Failed sentence #%s.\n %s" % (sID, traceback.format_exc())
                    logger.error(error_msg)
                    task.log_error(error_msg)
                    task.log_error("Failed annotation: %s" % str(annotation))
                    task.task_error_count += 1
            else:
                failed += 1
                error_msg = "Failed sentence #%s (%r not in %r)." % (sID, sID, hkeys)
                logger.error(error_msg)
                task.log_error(error_msg)
                task.log_error("Failed annotation: %s" % str(annotation))
                task.task_error_count += 1

    logger.info("Processed: %d." % processed)
    logger.info("Failed: %d." % failed)
    logger.info("Total: %d." % total)

    return request_body_dict


