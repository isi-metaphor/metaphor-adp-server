#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import re
import nltk

from collections import defaultdict

ss_for_s = {
    'ANIMAL': 'ACTION',
    'BODY_OF_WATER': 'MOVEMENT',
    'CONFINEMENT': 'EXIT',
    'ENSLAVEMENT': 'OPPRESSION',
    'MAZE': 'OBSTRUCTION',
    'PARASITE': 'DESTRUCTIVE_BEING',
    'PHYSICAL_BURDEN': 'RELIEF',
    'PHYSICAL_LOCATION': 'DEFINED_REGION',
    'DARKNESS': 'DARK_END_OF_RANGE_OF_DARKNESS_LIGHT',
    'LOW_POINT': 'MOVEMENT_DOWNWARD',
    'BUILDING': 'CREATION_DESTRUCTION',
    'MEDICINE': 'ADMINISTRATION',
    'MORAL_DUTY': 'REMUNERATION',
    'VERTICAL_SCALE': 'MOVEMENT_ON_THE_SCALE',
    'DESTROYER': 'DESTRUCTIVE_FORCE',
    'ENABLER': 'LUBRICANT',
    'OBESITY': 'EXCESS_CONSUMPTION',
    'RESOURCE': 'QUANTITY_SIZE',
    'VISION': 'SEEING',
    'HIGH_POINT': 'TOP_OF_ECONOMIC_SCALE',
    'LIGHT': 'LIGHT_END_OF_RANGE_OF_DARKNESS_LIGHT',
    'BLOOD_SYSTEM': 'MOVEMENT',
    'CROP': 'PLANTING',
    'FOOD': 'CONSUMPTION',
    'GAME': 'ACTIONS',
    'PLANT': 'CHANGE_OF_STATE',
    'PORTAL': 'MEANS_OF_ENTRY',
    'MOVEMENT_ON_A_VERTICAL_SCALE': 'MOVEMENT',
    'COMPETITION': 'COMPONENT',
    'HUMAN_BODY': 'COMPONENT',
    'MOVEMENT': 'MOVEMENT'
}


def find_indexes(sub_str, main_str):
    """Find index of `sub_str` in `main_str`."""

    if len(sub_str) == 0:
        return []

    inds = []
    ss_toks = nltk.word_tokenize(sub_str.rstrip().lower())
    ms_toks = nltk.word_tokenize(main_str.rstrip().lower())

    for mi, mt in enumerate(ms_toks):
        if ss_toks[0] == mt and len(ms_toks) >= mi + len(ss_toks) - 1:
            inds.append(mi)
            found = True
            if len(ss_toks) > 1:
                for si in range(1, len(ss_toks)):
                    if ss_toks[si] != ms_toks[mi + si]:
                        found = False
                        break
                    else:
                        inds.append(mi + si)
            if found:
                return inds
            else:
                inds = []

    return inds


# process parse output and generate index->argument dict
def extract_words_ids(parse):
    Wids = dict()
    obs_pattern = re.compile('\(([^\s\()]+)([^:\()]+):[^:]+:[^:]+:\[([\d,]+)\]\)')

    snumb = 1

    for match in obs_pattern.finditer(parse):
        pname = match.group(1)
        args = match.group(2).strip().split()
        pids = match.group(3).split(',')

        for pid in pids:
            if not pid.startswith(str(snumb)):
                snumb += 1
            tid = int(pid) - snumb * 1000

            if pname.endswith('-vb') or pname.endswith('-rb') or \
               pname.endswith('-adj') and len(args) > 0:
                Wids[tid] = [args[0]]
            elif pname.endswith('-nn') and len(args) > 1:
                Wids[tid] = [args[0], args[1]]

    return Wids


# Find prop arguments for input IDs
def find_args(inputIDs, wordIDs):
    oArgs = []

    for iid in inputIDs:
        wid = iid + 1
        if wid in wordIDs:
            oArgs += wordIDs[wid]

    return oArgs


def wordStr2print(Args, word_props, Equalities):
    output_str = ''

    words = []
    for arg in Args:
        newwords = find_words(arg, word_props, Equalities, False)
        for word in newwords:
            if word not in words:
                words.append(word)

    for word in words:
            output_str += word + ','

    if len(output_str) > 0:
        return output_str[:-1]
    return ''


def wordStr2print_Mapping(mappings, word_props, Equalities):
    output_str = ''

    for propName in mappings.keys():
        words = []

        firstargs = []
        for args in mappings[propName]:
            # for arg in args:
            # output only first ARG instead of all
            firstargs.append(args[0])
            newwords = find_words(args[0], word_props, Equalities, True)
            for word in newwords:
                if word not in words:
                    words.append(word)

        output_str += ', ' + propName + '['
        if len(words) > 0:
            for word in words:
                output_str += word + ','
        else:
            for arg in firstargs:
                output_str += arg + ','

        output_str = output_str[:-1] + ']'

    return output_str[2:]


def find_words(ARG, word_props, Equalities, is_mapping):
    all_args = []
    if is_mapping and ARG in Equalities:
        all_args = Equalities[ARG].keys()

    all_args.append(ARG)

    words = []
    for arg in all_args:
        if not arg.startswith('_') and not arg.startswith('u'):
            for (propName, args) in word_props:
                if arg == args[0] and (propName.endswith('-vb') or
                                       propName.endswith('-rb') or
                                       propName.endswith('-adj') or
                                       propName.endswith('-nn')):
                    if propName.endswith('-adj'):
                        if not propName[:-4] in words:
                            words.append(propName[:-4])
                    else:
                        if not propName[:-3] in words:
                            words.append(propName[:-3])
                elif len(args) > 1 and arg == args[1]:
                    if propName.endswith('-nn'):
                        if not propName[:-3] in words:
                            words.append(propName[:-3])
                    elif propName == 'person':
                        if 'person' not in words:
                            words.append('person')
                # TODO: enable when Boxer starts working correctly
                # elif propName == 'subset-of' and arg == args[2]:
                #    output_str += ',' + find_words(args[1], word_props, Equalities, is_mapping)

    if len(words) == 0 and is_mapping:
        return [ARG]

    return words


def create_d_struc(super_d, sub_d, input_vars, check_vars):
    outputstrucs = defaultdict(dict)

    for superd in super_d:
        for superArgs in super_d[superd]:
            includeD = True
            if check_vars:
                if not superArgs[0] in input_vars:
                    includeD = False

            if includeD and (superd not in outputstrucs or
                             superArgs[0] not in outputstrucs[superd]):
                outputstrucs[superd][superArgs[0]] = []

            for subd in sub_d:
                for subArgs in sub_d[subd]:
                    if len(subArgs) > 1 and superArgs[0] == subArgs[1]:
                        if check_vars:
                            if subArgs[0] in input_vars:
                                if not includeD:
                                    if superd not in outputstrucs or \
                                       superArgs[0] not in outputstrucs[superd]:
                                        outputstrucs[superd][superArgs[0]] = []
                                    includeD = True
                                outputstrucs[superd][superArgs[0]].append((subd, subArgs[0]))
                        else:
                            outputstrucs[superd][superArgs[0]].append((subd, subArgs[0]))

    return outputstrucs


def collectVars(struc, superkey, equalities):
    output = []

    for arg in struc[superkey]:
        if not arg.startswith('_') and arg not in output:
            output.append(arg)
            if arg in equalities:
                for a in equalities[arg]:
                    output.append(a)
        for (subd, subarg) in struc[superkey][arg]:
            if not subarg.startswith('_') and subarg not in output:
                output.append(subarg)
                if subarg in equalities:
                    for a in equalities[subarg]:
                        output.append(a)
    return output


def collectVars2(struc, domain, subdomain):
    output = dict()

    for arg in struc[domain]:
        if not arg.startswith('_'):
            output[arg] = 1

        for (subd, subarg) in struc[domain][arg]:
            if not subarg.startswith('_'):
                output[subarg] = 1

    return output


def is_linked_by_parse(v1, v2, word_props, equalities, input_been, path_len):
    if v1 == v2:
        return path_len

    path_len += 1
    if path_len == 9:
        return path_len

    been = list(input_been)
    if (v1, v2) in been:
        return 9
    been.append((v1, v2))
    been.append((v2, v1))

    nbrs = []
    for (propName, args) in word_props:
        if v1 in args:
            if v2 in args:
                return path_len

            for a in args:
                if a != v1:
                    nbrs.append(a)

    pl = 9
    for n in nbrs:
        npl = is_linked_by_parse(n, v2, word_props, equalities, been, path_len)
        if npl < pl:
            pl = npl
    return pl


def filter_mappings(BestArgs, mappings):
    best_mapping = dict()
    toremove = dict()

    for pred_name in mappings:
        for args in mappings[pred_name]:
            included = False
            for arg in args:
                if arg in BestArgs:
                    included = True
                    break
            if included:
                if pred_name not in best_mapping:
                    best_mapping[pred_name] = []
                best_mapping[pred_name].append(args)
            else:
                if pred_name not in toremove:
                    toremove[pred_name] = []
                toremove[pred_name].append(args)

    for pred_name in toremove:
        for args in toremove[pred_name]:
            included = False
            for arg in args:
                for pred_name2 in best_mapping:
                    for args2 in best_mapping[pred_name2]:
                        if arg in args2:
                            included = True
                            break
                    if included:
                        break
                if included:
                    break
            if included:
                if pred_name not in best_mapping:
                    best_mapping[pred_name] = []
                best_mapping[pred_name].append(args)

    return best_mapping


def transitive_closure(A):
    """Compute the transitive closure of a hash."""
    while True:
        newlink = False

        new_A = defaultdict(dict)
        for x in A.keys():
            for y in A[x].keys():
                for z in A[y].keys():
                    if x != z and z not in A[x]:
                        new_A[x][z] = 1
                        new_A[z][x] = 1
                        newlink = True

        if not newlink:
            break

        for x in new_A.keys():
            for y in new_A[x].keys():
                A[x][y] = 1

    return A


def extract_CM_mapping(sid, input_string, parse, description, lcc_annotation):
    sources = dict()
    subsources = dict()

    targets = dict()
    subtargets = dict()
    subsubtargets = dict()

    mappings = dict()

    roles = []
    word_props = []

    equalities = defaultdict(dict)

    source_task = False
    if lcc_annotation:
        if ("sourceFrame" in lcc_annotation and
            "targetFrame" in lcc_annotation and
            "targetConceptSubDomain" in lcc_annotation):
            if (lcc_annotation["sourceFrame"] and
                len(lcc_annotation["sourceFrame"]) > 0):
                if (lcc_annotation["targetConceptSubDomain"] and
                    len(lcc_annotation["targetConceptSubDomain"]) > 0):
                    if lcc_annotation["targetConceptSubDomain"] == 'DEBT':
                        lcc_annotation["targetConceptSubDomain"] = 'POVERTY'
                    elif lcc_annotation["targetConceptSubDomain"] == 'MONEY':
                        lcc_annotation["targetConceptSubDomain"] = 'WEALTH'

                    if (lcc_annotation["targetFrame"] and
                        len(lcc_annotation["targetFrame"]) > 0):
                        source_task = True

    prop_pattern = re.compile('([^\(]+)\(([^\)]+)\)')

    propositions = input_string.split(' ^ ')
    prop_list = []
    for item in propositions:
        prop_match_obj = prop_pattern.match(item)
        if prop_match_obj:
            prop_name = prop_match_obj.group(1)
            arg_str = prop_match_obj.group(2)
            args = arg_str.split(',')

            if prop_name.startswith('T#'):
                if prop_name[2:] not in targets:
                    targets[prop_name[2:]] = []
                if args not in targets[prop_name[2:]]:
                    targets[prop_name[2:]].append(args)
            elif prop_name.startswith('TS#'):
                dname = prop_name[3:]
                if (not source_task or
                    dname == lcc_annotation["targetConceptSubDomain"]):
                    if dname not in subtargets:
                        subtargets[dname] = []
                    if args not in subtargets[dname]:
                        subtargets[dname].append(args)
            elif prop_name.startswith('TSS#'):
                dname = prop_name[4:]
                if not source_task or dname == lcc_annotation["targetFrame"]:
                    if dname not in subsubtargets:
                        subsubtargets[dname] = []
                    if args not in subsubtargets[dname]:
                        subsubtargets[dname].append(args)
            elif prop_name.startswith('S#'):
                dname = prop_name[2:]
                if not source_task or dname == lcc_annotation["sourceFrame"]:
                    if dname not in sources:
                        sources[dname] = []
                    if args not in sources[dname]:
                        sources[dname].append(args)
            elif prop_name.startswith('SS#'):
                ss_data = prop_name[3:].split('%')
                if len(ss_data) > 1:
                    prop_name = ss_data[1]
                else:
                    prop_name = ss_data[0]

                if prop_name not in subsources:
                    subsources[prop_name] = []
                if args not in subsources[prop_name]:
                    subsources[prop_name].append(args)
            elif prop_name.startswith('M#'):
                mname = prop_name[2:]
                if mname not in mappings:
                    mappings[mname] = []
                if args not in mappings[mname]:
                    mappings[mname].append(args)
            elif prop_name.startswith('R#'):
                pass
            elif prop_name.startswith('I#'):
                pass
            elif prop_name == '=':
                for i in range(len(args)):
                    arg1 = args[i]
                    j = i + 1
                    while j < len(args):
                        arg2 = args[j]
                        equalities[arg1][arg2] = 1
                        equalities[arg2][arg1] = 1
                        j += 1
            elif prop_name == '!=':
                continue
            elif prop_name == 'equal':
                equalities[args[1]][args[2]] = 1
                equalities[args[2]][args[1]] = 1
            else:
                word_props.append((prop_name, args))

    # Transitive closure of equalities
    equalities = transitive_closure(equalities)

    # Find arguments for the input target and source words
    input_target_args = []
    input_source_args = []
    check_vars = False
    if lcc_annotation and 'annotationMappings' in lcc_annotation and \
       len(lcc_annotation['annotationMappings']) > 0:
        firstAnn = lcc_annotation['annotationMappings'][0]
        if 'target' in firstAnn and 'source' in firstAnn:
            check_vars = True
            inputSourceIds = find_indexes(firstAnn['source'],
                                         lcc_annotation['linguisticMetaphor'])
            inputTargetIds = find_indexes(firstAnn['target'],
                                         lcc_annotation['linguisticMetaphor'])

            # extract words with ids from parse
            Wids = extract_words_ids(parse)
            # find arguments for input and source target words
            input_target_args = find_args(inputTargetIds, Wids)
            input_source_args = find_args(inputSourceIds, Wids)

    target_strucs = create_d_struc(subtargets, subsubtargets, input_target_args,
                                   check_vars)
    source_strucs = create_d_struc(sources, subsources, input_source_args,
                                   check_vars)

    output = {}
    if not lcc_annotation:
        output["sid"] = sid
    output["isiDescription"] = description
    output["targetConceptDomain"] = "ECONOMIC_INEQUALITY"

    bestCM = ''
    bestlink = 0

    Tdomains = []
    Sdomains = []

    CMs = dict()

    for targetS in target_strucs:
        tV = collectVars(target_strucs, targetS, equalities)
        Tdomains = []

        for targ in target_strucs[targetS]:
            if len(target_strucs[targetS][targ]) == 0 and \
               (targetS, targetS) not in Tdomains:
                Tdomains.append((targetS, targetS))
            else:
                for (tsubd, tsubarg) in target_strucs[targetS][targ]:
                    if (targetS, tsubd) not in Tdomains:
                        Tdomains.append((targetS, tsubd))

        Sdomains = []
        bestSVars = []
        for sourceS in source_strucs:
            for sarg in source_strucs[sourceS]:
                for (ssubS, ssarg) in source_strucs[sourceS][sarg]:
                    sargs = [ssarg]
                    sargs += equalities[ssarg].keys()
                    link = 9
                    for tv in tV:
                        for sv in sargs:
                            newlink = is_linked_by_parse(tv, sv, word_props,
                                                      equalities, [], 0)
                            if newlink < link:
                                link = newlink
                                if newlink < 2:
                                    break
                        if link < 2:
                            break
                    Sdomains.append((sourceS, ssubS, (1 - 0.05 - 0.1 * link)))
                    for (t, ts) in Tdomains:
                        for (s, ss, c) in Sdomains:
                            TSpair = "%s,%s,%s,%s" % (t, ts, s, ss)
                            if TSpair in CMs:
                                if CMs[TSpair] < c:
                                    CMs[TSpair] = c
                            else:
                                CMs[TSpair] = c

                            if c > bestlink:
                                bestlink = c
                                bestCM = "%s,%s,%s,%s" % (t, ts, s, ss)

    if len(Tdomains) == 0 or len(Sdomains) == 0:
        if len(Tdomains) == 0:
            if source_task:
                Tdomains.append((lcc_annotation["targetConceptSubDomain"],
                                 lcc_annotation["targetFrame"]))
            else:
                Tdomains.append(('POVERTY', 'POVERTY'))

            if len(source_strucs) > 0:
                for sourceS in source_strucs:
                    if source_task and sourceS != lcc_annotation["sourceFrame"]:
                        continue

                    for sarg in source_strucs[sourceS]:
                        for (ssubS, ssarg) in source_strucs[sourceS][sarg]:
                            Sdomains.append((sourceS, ssubS, 0.001))

        if len(Sdomains) == 0:
            if source_task:
                if lcc_annotation["sourceFrame"] in ss_for_s:
                    Sdomains.append((lcc_annotation["sourceFrame"],
                                     ss_for_s[lcc_annotation["sourceFrame"]],
                                     0.001))
                else:
                    Sdomains.append((lcc_annotation["sourceFrame"],
                                     'TYPE', 0.001))
            else:
                Sdomains.append(('STRUGGLE', 'TYPE', 0.001))

        for (t, ts) in Tdomains:
            for (s, ss, c) in Sdomains:
                TSpair = "%s,%s,%s,%s" % (t, ts, s, ss)
                if TSpair in CMs:
                    if CMs[TSpair] < c:
                        CMs[TSpair] = c
                else:
                    CMs[TSpair] = c
                bestCM = "%s,%s,%s,%s" % (t, ts, s, ss)

    explanationAppendix = "\n%%BEGIN_CM_LIST\n"
    for TSpair in CMs.keys():
        explanationAppendix += "ECONOMIC_INEQUALITY,%s,%s\n" \
                               % (TSpair, CMs[TSpair])
    explanationAppendix += "%%END_CM_LIST"

    output['isiAbductiveExplanation'] \
        = input_string + explanationAppendix.encode("utf-8")
    output["targetConceptDomain"] = 'ECONOMIC_INEQUALITY'
    data = bestCM.split(',')
    output["targetConceptSubDomain"] = data[0]
    output["targetFrame"] = data[1]
    output["sourceFrame"] = data[2]
    if data[3] == '-':
        output["sourceConceptSubDomain"] = 'TYPE'
    else:
        output["sourceConceptSubDomain"] = data[3]

    target_args = collectVars2(target_strucs, data[0], data[1])
    source_args = collectVars2(source_strucs, data[2], data[3])

    mappings = filter_mappings(target_args.keys() + source_args.keys(), mappings)
    mapping_str = wordStr2print_Mapping(mappings, word_props, equalities)

    annotationMappings_struc = dict()
    annotationMappings_struc['explanation'] = mapping_str

    if not check_vars:
        targetWords = wordStr2print(target_args, word_props, ())
        sourceWords = wordStr2print(source_args, word_props, ())
        annotationMappings_struc['target'] = targetWords
        annotationMappings_struc['source'] = sourceWords
        if len(targetWords) > 0:
            annotationMappings_struc['targetInLm'] = True
        else:
            annotationMappings_struc['targetInLm'] = False
        if len(sourceWords) > 0:
            annotationMappings_struc['sourceInLm'] = True
        else:
            annotationMappings_struc['sourceInLm'] = False

    output['annotationMappings'] = [annotationMappings_struc]

    return output
