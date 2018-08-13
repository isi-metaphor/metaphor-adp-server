# coding: utf-8

# Copyright (C) University of Southern California (https://usc.edu)
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>
# URL: <https://nlg.isi.edu>
# For more information, see README.md
# For license information, see LICENSE

import imp
import time
import traceback
import re

from collections import defaultdict
from subprocess import Popen, PIPE

import pexpect
import sexpdata

import simplejson as json

from lccsrv.paths import *
import manage as mng


ENV = os.environ
INPUT_METAPHORS_COUNT = 0
KB_COMPILED = True

DESCRIPTION \
    = "Abductive engine output; " \
    "targetFrame: Is currently equal to targetConceptSubDomain;" \
    "targetConceptDomain: Target concept domain defined by abduction; " \
    "targetConceptSubDomain: Target concept subdomain defined by " \
    "abduction ; " \
    "sourceFrame: Source frame proposed by abduction ; " \
    "sourceConceptSubDomain: Source subdomain proposed by abduction ; " \
    "targetFrameElementSentence: List of words denoting the target found " \
    "by abduction; " \
    "sourceFrameElementSentence: List of words denoting the source found " \
    "by abduction; " \
    "annotationMappings: Target-Source mapping structures. " \
    "isiAbductiveExplanation: Target-Source mapping (metaphor " \
    "interpretation) as logical form found by abduction."


def extract_parses(input_string):
    output_dict = dict()
    pattern = re.compile(r'.+\(\s*name\s+([^\)]+)\)')
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
    global INPUT_METAPHORS_COUNT
    output_str = ""
    for key in input_metaphors.keys():
        output_str += "<META>" + key + "\n\n " + input_metaphors[key] + "\n\n"
        INPUT_METAPHORS_COUNT += 1
    return output_str


def strcut(some_str, max_size=120):
    if some_str is not None:
        some_str = str(some_str)
        if len(some_str) > max_size:
            return some_str[:max_size]
        return some_str
    return "<NONE>"


def fa_expect():
    index = CHILD['FA'].expect(
        [".*\r\n\r\n.*\r\n\r\n", pexpect.TIMEOUT, pexpect.EOF])
    index = CHILD['FA'].expect(
        ["END\r\n", pexpect.TIMEOUT, pexpect.EOF])
    index = CHILD['FA'].expect(
        [".*\r\n\r\n.*\r\n\r\nEND", pexpect.TIMEOUT, pexpect.EOF])
    return index


def es_expect():
    index = CHILD['ES'].expect(
        [".*\r\n\r\n.*\r\n\r\n.*\r\n\r\n", pexpect.TIMEOUT, pexpect.EOF])
    index = CHILD['ES'].expect(
        ["END\r\n", pexpect.TIMEOUT, pexpect.EOF])
    index = CHILD['ES'].expect(
        [".*\r\n\r\n.*\r\n\r\n.*\r\n\r\nEND", pexpect.TIMEOUT, pexpect.EOF])
    return index


def ru_expect():
    index = CHILD['RU'].expect(
        [".*\r\n\r\n.*\r\n\r\n.*\r\n\r\n", pexpect.TIMEOUT, pexpect.EOF])
    index = CHILD['RU'].expect(
        ["END\r\n", pexpect.TIMEOUT, pexpect.EOF])
    index = CHILD['RU'].expect(
        [".*\r\n\r\n.*\r\n\r\n.*\r\n\r\nEND", pexpect.TIMEOUT, pexpect.EOF])
    return index


def en_expect():
    index = CHILD['EN'].expect(
        [r"ccg\(.*\)*\)\)\.\r\n\r\nccg\(\d+.*'END', 'END', .*\)\)\.\r\n\r\n",
         pexpect.TIMEOUT, pexpect.EOF])

    # CHILD['EN'].expect(pexpect.EOF)
    return index
    # return 0


META_PATTERN = re.compile(r"^<META>[\s]*[0-9]+$")


def getWpos(tokenizer_output, language):
    word2ids = defaultdict(list)
    if language in ["ES", "FA", "RU"]:
        for line in tokenizer_output.splitlines():
            line = line.strip()
            if line:
                words = line.split()
                if words and len(words) > 1:
                    word2ids[words[1]].append(int(words[0]))
    elif language == "EN":
        for line in tokenizer_output.splitlines():
            line = line.strip()
            if line and not META_PATTERN.match(line):
                words = line.split()
                for i in xrange(len(words)):
                    word2ids[words[i]].append(i + 1)
    return word2ids


def remove_thousands(pid):
    if pid and type(pid) == int:
        while pid > 999:
            pid = pid - 1000
    return pid


idPattern = re.compile(r"^.*\[([^\]]+)\].*$")


def filter_parser_output(parses, word2ids, sources, targets):
    filtered = {}
    if sources and targets and parses and word2ids:
        for key in parses:
            allfound = False
            toKeep = set()
            if key in sources and key in targets and key in word2ids:
                allfound = True
                wids = word2ids[key]
                for w in sources[key].strip().split():
                    if w in wids:
                        toKeep.update(wids[w])
                    else:
                        allfound = False
                        break
                for w in targets[key].strip().split():
                    if w in wids:
                        toKeep.update(wids[w])
                    else:
                        allfound = False
                        break
            if allfound and toKeep:
                filtered[key] = "(O (name " + str(key) + ") (^ "
                o = sexpdata.loads(parses[key])
                for p in o[2]:
                    if type(p) == list:
                        # print("p: " + str(p))
                        pidstring = sexpdata.dumps(p[-1])
                        # print("pidstring: " + pidstring)
                        result = idPattern.match(pidstring)
                        keep_this_one = True
                        if result:
                            keep_this_one = False
                            pids = result.group(1).split(",")
                            for pid in pids:
                                try:
                                    pid = int(result.group(1)) \
                                          if result else None
                                    pid = remove_thousands(pid)
                                except ValueError:
                                    pid = None
                                # print("pid number: " + str(pid))
                                if not pid or pid in toKeep:
                                    keep_this_one = True
                                    break
                        if keep_this_one:
                            filtered[key] += print_pred(p)
                    # print("filtered[key]: " + filtered[key])
                filtered[key] += "))"
    parser_output = ""
    if parses:
        for key in parses:
            if key in filtered:
                parser_output += filtered[key] + "\n"
            else:
                parser_output += parses[key] + "\n"
    return parser_output


def need_to_generate_graph(dograph):
    if dograph == "NOGRAPH":
        return False
    if dograph == "SOLUTION":
        return True
    if dograph == "ALL":
        return True
    if dograph is True:
        return True
    return False


def print_pred(p):
    return sexpdata.dumps(p).replace(": [", ":[").encode("utf-8")


def merge_multiple_observations(parser_output):
    ret = parser_output
    if parser_output:
        lines = parser_output.splitlines()
        if lines and len(lines) > 1:
            ret = []
            counter = 0
            preds = [sexpdata.Symbol("^")]

            for l in lines:
                o = sexpdata.loads(l)
                if not ret:
                    ret.append(o[0])
                    ret.append(o[1])
                for p in o[2]:
                    if type(p) == list:
                        np = [p[0]]
                        for a in p[1:]:
                            if type(a) == sexpdata.Symbol:
                                n = a.value()
                                if n[0].islower():
                                    np.append(
                                        sexpdata.Symbol(
                                            a.value() + "_" + str(counter)
                                        )
                                    )
                                    continue
                            np.append(a)
                        preds.append(np)
                # print(sexpdata.dumps(o))
                counter += 1
            ret.append(preds)
            ret = print_pred(ret)
    return ret


CHILD = {'EN': '', 'ES': '', 'FA': '', 'RU': ''}

EXPECT_CHILD = {
    'EN': en_expect,
    'ES': es_expect,
    'FA': fa_expect,
    'RU': ru_expect
}


def run_annotation(request_body_dict, input_metaphors, language, task,
                   logger, with_pdf_content, last_step=3, kb=None, depth='3',
                   extractor=None, sources=None, targets=None):
    word2ids = defaultdict(list)
    extractor_module = None
    # Load up the extractor code to use for extracting the metaphor
    if extractor:
        module_desc = imp.find_module(extractor, ["legacy"])
        extractor_module = imp.load_module(extractor, *module_desc)
    global CHILD
    start_time = time.time()
    # input_str = generate_text_input(input_metaphors, language)
    INPUT_METAPHORS_COUNT = len(input_metaphors.keys())
    metaphor_count = 0
    tokenizer_proc = ""
    parser_proc = ""
    create_lf_proc = ""
    parser_output_append = ""
    b2h_proc = ""
    parser_output_inter = ""
    create_lf_output = ""

    # Parser pipeline
    if language == "EN":
        tokenizer_proc = BOXER_DIR + "/bin/tokkie --stdin"
        parser_proc = BOXER_DIR + "/bin/candc --models " + \
            BOXER_DIR + "/models/boxer --candc-printer boxer 2>null"
        create_lf_proc = BOXER_DIR + "/bin/boxer --semantics tacitus " + \
            "--resolve true --stdin"
        parser_output_append \
            = ":- op(601, xfx, (/)).\n:- op(601, xfx, (\\)).\n" + \
            ":- multifile ccg/2, id/2.\n:- discontiguous ccg/2, id/2.\n"
        b2h_proc = BOXER2HENRY + " --nonmerge sameid freqpred"
        kb_path = kb or EN_KB_PATH

    elif language == "ES":
        malt_parser_dir = os.path.join(METAPHOR_DIR,
                                       "external-tools/malt-1.7.2")
        parser_args = "-c ancora_under40 -m parse -w " + \
            malt_parser_dir + " -lfi parser-es.log"
        tokenizer_proc = METAPHOR_DIR + "/pipelines/Spanish/preproc.sh"
        parser_proc = "java -Xmx16g " + \
                      "-cp " + malt_parser_dir + "/maltparser-1.7.2.jar:" + \
                      malt_parser_dir + " MaltParserWrapService " + parser_args
        create_lf_proc = METAPHOR_DIR + "/pipelines/Spanish/create-lf.sh"
        parser_output_append = ""
        b2h_proc = PARSER2HENRY + " --nonmerge sameid freqpred"
        kb_path = kb or ES_KB_PATH

    elif language == "FA":
        malt_parser_dir = os.path.join(METAPHOR_DIR, "external-tools/malt-1.5")
        parser_args = "-c farsiMALTModel -m parse -w " + \
                      malt_parser_dir + " -lfi parser-fa.log"
        tokenizer_proc = METAPHOR_DIR + "/pipelines/Farsi/preproc.sh"
        parser_proc = "java -Xmx16g " + \
                      "-cp " + malt_parser_dir + "/dist/malt/malt.jar:" + \
                      malt_parser_dir + " MaltParserWrapService " + parser_args
        create_lf_proc = METAPHOR_DIR + "/pipelines/Farsi/create-lf.sh"
        parser_output_append = ""
        b2h_proc = PARSER2HENRY + " --nonmerge sameid freqpred"
        kb_path = kb or FA_KB_PATH

    elif language == "RU":
        malt_parser_dir = os.path.join(METAPHOR_DIR, "external-tools/malt-1.5")
        parser_args = "-c rus-test -m parse -w " + malt_parser_dir + \
                      " -lfi parser-ru.log"
        tokenizer_proc = METAPHOR_DIR + "/pipelines/Russian/preproc.sh"
        parser_proc = "java -Xmx16g " + \
                      "-cp " + malt_parser_dir + "/dist/malt/malt.jar:" + \
                      malt_parser_dir + " MaltParserWrapService " + parser_args
        create_lf_proc = METAPHOR_DIR + "/pipelines/Russian/create-lf.sh"
        parser_output_append = ""
        b2h_proc = PARSER2HENRY + " --nonmerge sameid freqpred"
        kb_path = kb or RU_KB_PATH

    parser_start_time = time.time()
    annotations = request_body_dict["metaphorAnnotationRecords"]
    while True:
        if mng.get_parser_lock(language):
            mng.set_parser_lock(language, False)
            for key in input_metaphors.keys():
                metaphor_count += 1
                if "parser_output" in annotations[metaphor_count - 1] and \
                   annotations[metaphor_count - 1]["parser_output"] != "":
                    create_lf_output \
                        += annotations[metaphor_count - 1]["parser_output"]
                    continue

                input_str = "<META>" + str(key) + "\n\n" + input_metaphors[key]
                if language == "EN":
                    input_str += "\n"
                else:
                    input_str += "\n\n"
                logger.info("Processing metaphor " + str(metaphor_count))
                logger.info("Running tokenizing command: '%s'." %
                            tokenizer_proc)
                logger.info("Input: %s" % input_str)
                task.log_error("Input: %r" % input_str)
                tokenizer_pipeline = Popen(
                    tokenizer_proc,
                    env=ENV,
                    shell=True,
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=None,
                    close_fds=True
                )
                tokenizer_output, tokenizer_stderr \
                    = tokenizer_pipeline.communicate(input=input_str)

                if language == "EN":
                    # lines = ""
                    # lines = tokenizer_output.replace("\n", " ")
                    # lines = lines.rstrip()
                    # lines = re.sub(r'(<META>)(\d+)(\s)', r'\1\2\n\n', lines)
                    tokenizer_output += "END\n\n"

                logger.info("Tokenizer output:\n%s" % tokenizer_output)
                task.log_error("Tokenizer output:\n%r" % tokenizer_output)
                word2ids[key] = getWpos(tokenizer_output, language)

                logger.info("Running parsing command: '%s'." % parser_proc)
                logger.info("Input: %s" % tokenizer_output)
                logger.info(language + " parser running: " +
                            str(mng.get_parser_status(language)))
                if not mng.get_parser_status(language):
                    CHILD[language] = pexpect.spawn(
                        '/bin/bash', ['-c', parser_proc], timeout=30)
                    mng.set_parser_status(language, True)

                CHILD[language].send(tokenizer_output)
                reattempts = 0
                while reattempts < 2:
                    logger.info(language + " re-attempts: %d\n" % reattempts)
                    index = EXPECT_CHILD[language]()
                    if index == 0:
                        parser_output_inter = CHILD[language].after
                        try:
                            junk = CHILD[language].stdout.readlines()
                        except Exception:
                            junk = ""
                        if not language == "EN":
                            parser_output_inter \
                                = parser_output_append + parser_output_inter
                            parser_output_inter \
                                = parser_output_inter.replace("END", "")
                        break
                    elif reattempts == 0:
                        # logger.info("child before: " +
                        #             CHILD[language].before + "\n")
                        reattempts += 1
                        CHILD[language].terminate()
                        CHILD[language] = pexpect.spawn(
                            '/bin/bash', ['-c', parser_proc], timeout=30)
                        CHILD[language].send(tokenizer_output)
                    else:
                        logger.info(language + " parser not working.\n")
                        task.log_error("\n" + language +
                                       " parser not working.\n")
                        reattempts = 2
                        CHILD[language].terminate()
                        mng.set_parser_status(language, False)
                logger.info("Parser flag: " + str(mng.get_parser_flag()))
                if not mng.get_parser_flag():
                    logger.info("\nTerminating " + language +
                                " parser process.\n")
                    CHILD[language].terminate()
                    CHILD[language] = ""
                    mng.set_parser_status(language, False)

                if language == "EN":
                    parser_output_inter = re.sub("\n", "\t",
                                                 parser_output_inter)
                    # parser_output_inter = re.sub("ccg\(\d+", "ccg(1",
                    #                              parser_output_inter)
                    regex = r'(ccg\(.*\)\.\r\t\r\t)'
                    ccgs = re.findall(regex, parser_output_inter)
                    if ccgs:
                        logger.info("separate ccgs: " + str(ccgs))
                        task.log_error("ccgs[0].split()" +
                                       str(ccgs[0].split("\r\t\r\t")))
                        logger.info("separate ccgs: " + str(ccgs))
                        task.log_error("ccgs[0].split()" +
                                       str(ccgs[0].split("\r\t\r\t")))
                        final_parser_output = parser_output_append
                        ccg_split = ccgs[0].split("\r\t\r\t")
                        for i in range(len(ccg_split) - 2):
                            ccg_replace = "ccg(" + str(i+1)
                            ccg_split[i] = re.sub(r"ccg\(\d+", ccg_replace,
                                                  ccg_split[i])
                            ccg_split[i] = re.sub("\t", "\n", ccg_split[i])
                            final_parser_output += ccg_split[i] + "\r\n\r\n"
                            final_parser_output += "id(" + str(key) + \
                                                   ",[" + str(i + 1) + \
                                                   "]).\r\n\r\n"
                        parser_output_inter = final_parser_output

                if language == "ES":
                    parser_output_inter \
                        = parser_output_inter.replace("ROOT", "sentence")
                logger.info("Parser output:\n%r" % parser_output_inter)
                task.log_error("Parser output:\n%r" % parser_output_inter)

                logger.info("Running createLF command: '%s'." % create_lf_proc)
                logger.info("Input: %s" % parser_output_inter)

                create_lf_pipeline = Popen(
                    create_lf_proc,
                    env=ENV,
                    shell=True,
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=None,
                    close_fds=True
                )
                create_lf_output_temp, create_lf_stderr_tmp \
                    = create_lf_pipeline.communicate(input=parser_output_inter)
                if "parser_output" in annotations[metaphor_count-1]:
                    annotations[metaphor_count-1]["parser_output"] \
                        = create_lf_output_temp
                create_lf_output += create_lf_output_temp
            mng.set_parser_lock(language, True)
            break

    parser_end_time = time.time()
    logger.info("createLF output:\n%s" % create_lf_output)
    task.log_error("createLF output:\n%r" % create_lf_output)
    if "parser_time" in request_body_dict:
        request_body_dict["parser_time"] \
            = str((parser_end_time - parser_start_time))
    logger.info("Running boxer-to-henry command: '%s'." % b2h_proc)
    logger.info("Input: %s" % create_lf_output)
    b2h_pipeline = Popen(
        b2h_proc,
        env=ENV,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=None,
        close_fds=True
    )
    parser_output, parser_stderr = b2h_pipeline.communicate(
        input=create_lf_output)
    logger.info("B2H output:\n%s\n" % parser_output)
    task.log_error("B2H output: \n%r" % parser_output)
    parser_output = merge_multiple_observations(parser_output)
    logger.info("B2H output after merging:\n%s\n" % parser_output)
    task.log_error("B2H output after merging: \n%r" % parser_output)
    task.parse_out = parser_output
    # Parser processing time in seconds
    parser_time = (time.time() - start_time) * 0.001
    logger.info("Command finished. Processing time: %r." % parser_time)
    if last_step == 1:
        task.henry_out = " "
        task.dot_out = " "
        result = json.dumps(request_body_dict, encoding="utf-8", indent=2)
        return result

    parses = extract_parses(parser_output)
    logger.info("Parses:\n%r\n" % parses)
    task.log_error("Parses:\n%r" % parses)

    msg = "Initial parser output: \n" + str(parses) + "\n sources: " + \
          str(sources) + "\n targets: " + str(targets) + "\n word2ids: " + \
          str(word2ids)
    logger.info(msg)
    task.log_error(msg)

    parser_output = filter_parser_output(parses, word2ids, sources, targets)
    msg = "Final parser output: \n" + parser_output
    logger.info(msg)
    task.log_error(msg)

    henry_start_time = time.time()

    # Time to generate final output in seconds
    generate_output_time = 2

    # Time left for Henry in seconds
    time_all_henry = 122 - generate_output_time

    if need_to_generate_graph(with_pdf_content):
        # Time for graph generation subtracted from Henry time in seconds
        time_all_henry += 3

    # Time for one interpretation in Henry in seconds
    time_unit_henry = str(int(time_all_henry / len(input_metaphors)))
    if time_unit_henry < 20:
        time_unit_henry = 20

    # Henry processing
    if KB_COMPILED:
        henry_proc = (
            HENRY_DIR + "/bin/henry " +
            "-m infer " +
            "-e " + HENRY_DIR + "/models/h93.py " +
            "-d " + depth +
            " -t 4 " +
            "-O proofgraph,statistics " +
            "-T " +  time_unit_henry +
            " -b " + kb_path
        )
    else:
        henry_proc = (
            HENRY_DIR + "/bin/henry " +
            "-m infer " +
            "-e " + HENRY_DIR + "/models/h93.py " +
            "-d " + depth +
            " -t 4 " +
            "-O proofgraph,statistics " +
            "-T " + time_unit_henry
        )

    logger.info("Running Henry command: '%s'." % henry_proc)
    henry_pipeline = Popen(
        henry_proc,
        env=ENV,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=None,
        close_fds=True
    )
    henry_output, henry_stderr \
        = henry_pipeline.communicate(input=parser_output)
    hypotheses = extract_hypotheses(henry_output)
    logger.info("Henry output:\n%s\n" % str(henry_output))
    task.log_error("Henry output: \n%r" % henry_output)
    task.henry_out = henry_output
    logger.info("Hypotheses output:\n%s\n" % hypotheses)
    task.log_error("Hypotheses: \n%r" % hypotheses)
    henry_end_time = time.time()

    if "henry_time" in request_body_dict:
        request_body_dict["henry_time"] \
            = str((henry_end_time - henry_start_time))

    if last_step == 2:
        return json.dumps(henry_output, encoding="utf-8", indent=2)

    processed, failed, empty = 0, 0, 0

    # Merge ADP result and input JSON document
    input_annotations = request_body_dict["metaphorAnnotationRecords"]

    if need_to_generate_graph(with_pdf_content):
        logger.info("Generating proofgraphs.")
        unique_id = get_unique_id()
        logger.info("unique id: %s\n" % unique_id)
        proofgraphs = generate_graph(input_metaphors, henry_output,
                                     unique_id, with_pdf_content)
        task.dot_out = proofgraphs

    logger.info("Input annotations count:\n%r\n" % len(input_annotations))

    total = len(input_annotations)
    hkeys = frozenset(hypotheses.keys())

    for annotation in input_annotations:
        if u"sentenceId" in annotation:
            sID = str(annotation["sentenceId"])
            if sID in hkeys:
                cm_output = extractor_module.extract_CM_mapping(
                    sID, hypotheses[sID], parses[sID], DESCRIPTION, annotation)
                msg = "Sentence #%s has interpretation #%s" % \
                      (sID, cm_output['isiAbductiveExplanation'])
                logger.info(msg)
                task.log_error(msg)
                try:
                    for annot_property in cm_output.keys():
                        if cm_output.get(annot_property):
                            annotation[annot_property] \
                                = cm_output[annot_property]
                    processed += 1
                    logger.info("Processed sentence #%s." % sID)

                except Exception:
                    failed += 1
                    error_msg = "Failed sentence #%s.\n %s" % (
                        sID,
                        traceback.format_exc()
                    )
                    logger.error(error_msg)
                    task.log_error(error_msg)
                    task.log_error("Failed annotation: %s" % str(annotation))
                    task.task_error_count += 1
            else:
                failed += 1
                error_msg = "Failed sentence #%s (%r not in %r)." % \
                            (sID, sID, hkeys)
                logger.error(error_msg)
                task.log_error(error_msg)
                task.log_error("Failed annotation: %s" % str(annotation))
                task.task_error_count += 1
    task.log_error("Parser output: \n%r" % parser_output)

    answer = dict()
    count = 0
    for annotation in input_annotations:
        if u"sentenceId" in annotation:
            sID = str(annotation["sentenceId"])
            if sID in hkeys:
                count = count + 1
                exp = str(annotation["isiAbductiveExplanation"])
                lines = exp.split('\n')
                start = False
                for line in lines:
                    if line == "%%BEGIN_CM_LIST":
                        start = True
                    elif line == "%%END_CM_LIST":
                        start = False
                    elif start:
                        r = line.split(',')
                        if len(r) == 6:
                            key = ",".join(r[0:5])
                            value = float(r[5])
                            if key in answer:
                                answer[key] += value
                            else:
                                answer[key] = value
    msg = "number of sentences: %d" % count
    logger.info(msg)
    task.log_error(msg)
    msg = "raw cumulative result: %r" % answer
    logger.info(msg)
    task.log_error(msg)
    for key in answer:
        answer[key] /= count
    best = -1
    bestkey = ''
    if answer:
        for key in answer:
            if answer[key] >= best:
                best = answer[key]
                bestkey = key
        msg = "best: %s,%s" % (bestkey, best)
        logger.info(msg)
        task.log_error(msg)
        for annotation in input_annotations:
            if u"isiAbductiveExplanation" in annotation:
                exp = str(annotation["isiAbductiveExplanation"])
                start = -1
                end = -1
                lines = exp.split('\n')
                for idx, line in enumerate(lines):
                    if line == "%%BEGIN_CM_LIST":
                        start = idx
                    elif line == "%%END_CM_LIST":
                        end = idx
                        break
                if start >= 0 and end >= 0:
                    exp = "\n".join(lines[0:start + 1] +
                                    [bestkey + "," + repr(best)] +
                                    [lines[end]])
                else:
                    exp += "\n%%BEGIN_CM_LIST\n" + bestkey + "," + \
                           repr(best) + "\n%%END_CM_LIST"
                msg = "Changing interpretation from:\n%s\n to:\n%s" % (
                    annotation["isiAbductiveExplanation"],
                    exp
                )
                logger.info(msg)
                task.log_error(msg)
                annotation["isiAbductiveExplanation"] = exp
                data = bestkey.split(',')

                def get_element(d, n):
                    if len(d) > n:
                        return d[n]
                    return ""

                annotation["targetConceptDomain"] = get_element(data, 0)
                annotation["targetConceptSubDomain"] = get_element(data, 1)
                annotation["targetFrame"] = get_element(data, 2)
                annotation["sourceFrame"] = get_element(data, 3)
                annotation["sourceConceptSubDomain"] = get_element(data, 4)

    # request_body_dict["kb"] = kb_path

    # Remove JSON debugging fields from JSON.
    if "kb" in request_body_dict:
        del request_body_dict["kb"]
    if "step" in request_body_dict:
        del request_body_dict["step"]
    if "task_id" in request_body_dict:
        request_body_dict["task_id"] = task.id
    if "enableDebug" in request_body_dict:
        del request_body_dict["enableDebug"]

    # task_id contains the id used to access the log entry for this request.
    if "task_id" in request_body_dict:
        request_body_dict["task_id"] = task.id

    result = json.dumps(request_body_dict, encoding="utf-8", indent=2)
    logger.info("Processed: %d." % processed)
    logger.info("Failed: %d." % failed)
    logger.info("Total: %d." % total)
    logger.info("Result size: %d." % len(result))

    return result


def generate_graph(input_dict, henry_output, unique_id, graphtype):
    # Create proofgraphs directory if it doesn't exist
    graph_dir = TMP_DIR + "/proofgraphs"

    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)

    out_data = {}

    for key in input_dict.keys():
        print "Generating a proofgraph for " + key
        graph_output = os.path.join(graph_dir, unique_id + "_" + key + ".pdf")

        if graphtype == "ALL":
            viz = "python2.7 " + HENRY_DIR + "/tools/proofgraph.py " + \
                  "--potential --graph " + key + " | dot -T png > " + \
                  graph_output
        else:
            viz = "python2.7 " + HENRY_DIR + "/tools/proofgraph.py " + \
                  "--graph " + key + " | dot -T png > " + graph_output

        graphical_processing = Popen(
            viz,
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=None,
            close_fds=True
        )

        graphical_processing.communicate(input=henry_output)
        # print "sleep"
        # time.sleep(3)

        with open(graph_output, "rb") as fl:
            out_data[key] = fl.read().encode("base64")

    return out_data


def get_unique_id():
    current_time = int(time.time())
    unique_id = str(current_time)[5:]
    return unique_id
