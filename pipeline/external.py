# coding: utf-8

# Copyright (C) University of Southern California (http://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <http://nlg.isi.edu/>
# For more information, see README.md
# For license information, see LICENSE

import time
import simplejson as json
import traceback

from lccsrv.paths import *
from legacy.extractor import *
from subprocess import Popen, PIPE
from manage import getParse, setParse
import pexpect
import re

child = ""

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


def strcut(some_str, max_size=120):
    if some_str is not None:
        some_str = str(some_str)
        if len(some_str) > max_size:
            return some_str[:max_size]
        return some_str
    return "<NONE>"


def run_annotation(request_body_dict, input_metaphors, language, task, logger, with_pdf_content, last_step=3, kb=None):
    start_time = time.time()
    input_str = generate_text_input(input_metaphors, language)
    global child
    # Parser pipeline
    parser_proc = ""
    if language == "FA":
        if last_step == 1:
            parser_proc = FARSI_PIPELINE
        else:
            parser_proc = FARSI_PIPELINE + " | python " + PARSER2HENRY + " --nonmerge sameid freqpred"
        if kb is None:
            KBPATH = FA_KBPATH
        else:
            KBPATH = kb

    elif language == "ES":
        if last_step == 1:
            parser_proc = SPANISH_PIPELINE
        else:
            parser_proc = SPANISH_PIPELINE + " | python " + PARSER2HENRY + " --nonmerge sameid freqpred"
        if kb is None:
            KBPATH = ES_KBPATH
        else:
            KBPATH = kb

    elif language == "RU":
        if last_step == 1:
            parser_proc = RUSSIAN_PIPELINE
        else:
            parser_proc = RUSSIAN_PIPELINE + " | python " + PARSER2HENRY + " --nonmerge sameid freqpred"
        if kb is None:
            KBPATH = RU_KBPATH
        else:
            KBPATH = kb

    elif language == "EN":
        tokenizer = BOXER_DIR + "/bin/tokkie --stdin"
        candcParser = BOXER_DIR + "/bin/candc --models " + BOXER_DIR + "/models/boxer --candc-printer boxer"
        boxer = BOXER_DIR + "/bin/boxer --semantics tacitus --resolve true --stdin"
        b2h = "python " + BOXER2HENRY + " --nonmerge sameid freqpred"
##        if last_step == 1:
##            parser_proc = tokenizer + " | " + candcParser + " | " + boxer
##        else:
##            parser_proc = tokenizer + " | " + candcParser + " | " + boxer + " | " + b2h
        
        if kb is None:
            KBPATH = EN_KBPATH
        else:
            KBPATH = kb
        tokenizer_proc = tokenizer
        logger.info("Running tokenizing command: '%s'." % tokenizer_proc)
        logger.info("Input str: %r" % strcut(input_str))
        tokenizer_pipeline = Popen(tokenizer_proc,
                                    env=ENV,
                                    shell=True,
                                    stdin=PIPE,
                                    stdout=PIPE,
                                    stderr=None,
                                    close_fds=True)
        tokenizer_output, tokenizer_stderr = tokenizer_pipeline.communicate(input=input_str)
	logger.info("Tokenizer Output:\n%r" % tokenizer_output)
	task.log_error("Tokenizer Output:\n%r" % tokenizer_output)
        #parser_proc = candcParser + " | " + boxer
	parser_proc = candcParser
        logger.info("Running parsing command: '%s'." % parser_proc)
        logger.info("Input str: %r" % strcut(tokenizer_output))
        start_time = time.time()
        """parser_pipeline = Popen(parser_proc,
                                env=ENV,
                                shell=True,
                                stdin=PIPE,
                                stdout=PIPE,
                                stderr=None,
                                close_fds=True)
                                
	parser_output_inter, parser_stderr_inter = parser_pipeline.communicate(input=tokenizer_output)"""
	task.log_error("Parser Running: %r " % getParse())
	
	if not getParse():
		child = pexpect.spawn(parser_proc,timeout=10)
		setParse(True)

	child.sendline(tokenizer_output)
	reattempts = 0
	parser_output_inter = ""
	while reattempts < 2:
		index = child.expect (["\n?ccg\(.*'+\)*\)\)\.\r\n", pexpect.TIMEOUT, pexpect.EOF])
		logger.info("reattempts: %r\n" % str(reattempts))
		if index == 0:
			parser_output_inter = child.after
			reattempts = 2
		elif reattempts == 0:
			reattempts += 1
			child.terminate()
			child = pexpect.spawn(parser_proc,timeout=10)
			child.sendline(tokenizer_output)
		else:
			logger.info("Parser not wroking\n")
			task.log_error("\nParser not working\n")
			reattempts = 2
			child.terminate()
			setParse(False)
	parser_output_inter = re.sub("ccg\(\d+", "ccg(1", parser_output_inter)
	
        logger.info("Parser output:\n%r" % parser_output_inter)
	task.log_error("Parser output:\n%r" % parser_output_inter)
        # Parser processing time in seconds
        parser_time = (time.time() - start_time) * 0.001
        logger.info("Command finished. Processing time: %r." % parser_time)
	boxer_proc = boxer
	logger.info("Running Boxer command: '%s'." % boxer_proc)
	logger.info("Input str: %r" % strcut(parser_output_inter)) 	
	parser_output_append = ":- op(601, xfx, (/)).\n:- op(601, xfx, (\)).\n:- multifile ccg/2, id/2.\n:- discontiguous ccg/2, id/2.\n"
	parser_output_append += parser_output_inter
	boxer_pipeline = Popen(boxer_proc,
        		       env=ENV,
	                       shell=True,
                               stdin=PIPE,
                               stdout=PIPE,
                               stderr=None,
                               close_fds=True)
	boxer_output, boxer_error = boxer_pipeline.communicate(input=parser_output_append)
	logger.info("Boxer output:\n%r" % boxer_output)
	task.log_error("Boxer output:\n%r" % boxer_output)
        b2h_proc = b2h
        logger.info("Running boxer-2-henry command: '%s'." % b2h_proc)
        logger.info("Input str: %r" % strcut(boxer_output))
        b2h_pipeline = Popen(b2h_proc,
                            env=ENV,
                            shell=True,
                            stdin=PIPE,
                            stdout=PIPE,
                            stderr=None,
                            close_fds=True)
        parser_output, parser_stderr = b2h_pipeline.communicate(input=boxer_output)
	logger.info("B2H output:\n%s\n" % parser_output)
    	task.log_error("B2H output: \n%r" % parser_output)
    	task.parse_out = parser_output


    if last_step == 1:
        return parser_output

    parses = extract_parses(parser_output)
    logger.info("Parses:\n%r\n" % strcut(parses))
    task.log_error("Parses:\n%r" % parses)

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
        henry_proc = HENRY_DIR + "/bin/henry -m infer -e " + HENRY_DIR +        \
                     "/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T " +  \
                     time_unit_henry + " -b " + KBPATH
    else:
        henry_proc = HENRY_DIR + "/bin/henry -m infer -e " + HENRY_DIR +        \
                     "/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T " +  \
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
    logger.info("Henry output:\n%s\n" % str(henry_output))
    task.log_error("Henry output: \n%r" % henry_output)
    task.henry_out = henry_output
    logger.info("Hypotheses output:\n%s\n" % strcut(hypotheses))
    task.log_error("Hypotheses: \n%r" % hypotheses)

    if last_step == 2:
        return json.dumps(henry_output, encoding="utf-8", indent=4)

    processed, failed, empty = 0, 0, 0

    # merge ADB result and input json document
    input_annotations = request_body_dict["metaphorAnnotationRecords"]


    if with_pdf_content:
        logger.info("Generating proofgraphs.")
        unique_id = get_unique_id()
	logger.info("unique id: %s\n" % unique_id) 
        proofgraphs = generate_graph(input_metaphors, henry_output, unique_id)
        task.dot_out = proofgraphs

    logger.info("Input annotations count:\n%r\n" % len(input_annotations))

    total = len(input_annotations)
    hkeys = frozenset(hypotheses.keys())

    for annotation in input_annotations:
        if u"sentenceId" in annotation:
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

    request_body_dict["kb"] = KBPATH
    result = json.dumps(request_body_dict, encoding="utf-8", indent=4)

    logger.info("Processed: %d." % processed)
    logger.info("Failed: %d." % failed)
    logger.info("Total: %d." % total)
    logger.info("Result size: %d." % len(result))

    return result



def generate_graph(input_dict, henry_output, unique_id):

    # create proofgraphs directory if it doesn't exist
    graph_dir = TMP_DIR + "/proofgraphs"

    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)

    out_data = {}

    for key in input_dict.keys():
        print "Generating a proofgraph for " + key
        graph_output = os.path.join(graph_dir, unique_id + "_" + key + ".pdf")

        viz = "python " + HENRY_DIR + "/tools/proofgraph.py --graph " + key + \
              " | dot -T png > " + graph_output

        graphical_processing = Popen(viz, shell=True, stdin=PIPE, stdout=PIPE,
                                     stderr=None, close_fds=True)

        graphical_processing.communicate(input=henry_output)
        #print "sleep"
        #time.sleep(3)

        with open(graph_output, "rb") as fl:
           out_data[key] = fl.read().encode("base64")

    return out_data


def get_unique_id():
    current_time = int(time.time())
    unique_id = str(current_time)[5:]
    return unique_id

