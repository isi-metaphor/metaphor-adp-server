#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import re

from collections import defaultdict


def printerr(*objs):
    print("", *objs, file=sys.stderr)


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


# hash with key the domain(subdomain) and value ta list of list of arguments
# output <domain,<domain_arg,((subdomain,subdomain_arg)...)>>
def create_d_struc(super_d, sub_d):
    output = defaultdict(dict)

    for superd in super_d:
        for super_args in super_d[superd]:
            if (
                superd not in output
                or super_args[0] not in output[superd]
            ):
                output[superd][super_args[0]] = []

            if sub_d:
                for subd in sub_d:
                    for sub_args in sub_d[subd]:
                        if len(sub_args) > 1 and super_args[0] == sub_args[1]:
                            output[superd][super_args[0]].append(
                                (subd, sub_args[0]))
            else:
                output[superd][super_args[0]].append(("", super_args[0]))
    return output


# returns the list of variables in the target-subtarget pair
def collect_vars(struc, superkey, equalities):
    output = []

    for arg in struc[superkey]:
        if not arg.startswith("_") and arg not in output:
            output.append(arg)
            if arg in equalities:
                for a in equalities[arg]:
                    output.append(a)
        for (subd, subarg) in struc[superkey][arg]:
            if not subarg.startswith("_") and subarg not in output:
                output.append(subarg)
                if subarg in equalities:
                    for a in equalities[subarg]:
                        output.append(a)
    return output


# Given two sets of arguments and the equalities, return the minimum
# distance between any of the variables in the two sets.
# - s_all: all the variables visited till now
# - s_end: second set increased by equalities
# - s_current: current set of variables
# - s_current: first set
# - increase s_current with equalities
# - if s_current contains one variable of s_end terminate and return current
#   path length.
#   - find all predications that use a variable of s_current, get the other
#     arguments
#   - remove from the other variables the variable already in s_current
#   - add the remaining to the s_new set
# - increase current path length
# - loop using s_new as s_current
# - terminate if after 9 iterations the s_end has not been reached or if s_new
#   is empty. (return in both cases the max of 9)
def test(vs1, vsend, equalities, other_vars, path_len=0):
    if not vs1 or not vsend:
        return 9
    if path_len >= 9:
        return path_len
    for x in vs1:
        if x in equalities:
            vs1.union(equalities[x].keys())
    if any(x in vs1 for x in vsend):
        return path_len
    path_len += 1
    vs1_new = set()
    for x in vs1:
        if x in other_vars:
            vs1_new.update(other_vars[x])
    for x in vs1:
        if x in vs1_new:
            vs1_new.remove(x)
    return test(vs1_new, vsend, equalities, other_vars, path_len)


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
    for (prop_name, args) in word_props:
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


def extract_CM_mapping(sid, input_string, parse, description, lcc_annotation):
    # input_string: the abduction output
    # parse: the parser output
    # description: the description of how to interpret the ISI output
    # lcc_annotation: input json request

    sources = defaultdict(list)
    subsources = defaultdict(list)

    targets = defaultdict(list)
    subtargets = defaultdict(list)
    subsubtargets = defaultdict(list)

    mappings = defaultdict(list)

    roles = []
    word_props = []

    equalities = defaultdict(dict)
    other_args = defaultdict(set)

    prop_pattern = re.compile('([^\(]+)\(([^\)]+)\)')

    # Process the input
    propositions = input_string.split(' ^ ')
    prop_list = []
    for item in propositions:
        prop_match_obj = prop_pattern.match(item)
        if not prop_match_obj:
            continue
        prop_name = prop_match_obj.group(1)
        arg_str = prop_match_obj.group(2)
        args = arg_str.split(',')

        if prop_name.startswith('T#'):
            dname = prop_name[2:]
            if args not in targets[dname]:
                targets[dname].append(args)
        elif prop_name.startswith('TS#'):
            dname = prop_name[3:]
            if args not in subtargets[dname]:
                subtargets[dname].append(args)
        elif prop_name.startswith('TSS#'):
            dname = prop_name[4:]
            if args not in subsubtargets[dname]:
                subsubtargets[dname].append(args)
        elif prop_name.startswith('S#'):
            dname = prop_name[2:]
            if args not in sources[dname]:
                sources[dname].append(args)
        elif prop_name.startswith('SS#'):
            ss_data = prop_name[3:].split('%')
            if len(ss_data) > 1:
                prop_name = ss_data[1]
            else:
                prop_name = ss_data[0]

            if args not in subsources[prop_name]:
                subsources[prop_name].append(args)
        elif prop_name.startswith('M#'):
            mname = prop_name[2:]
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
            uargs = set(args)
            for a in uargs:
                other_args[a] |= uargs

    # Transitive closure of equalities
    equalities = transitive_closure(equalities)

    target_strucs = create_d_struc(subtargets, subsubtargets)
    source_strucs = create_d_struc(sources, subsources)

    output = {
        "isiDescription": description,
        "isiAbductiveExplanation": input_string,
        "sourceConceptSubDomain": "",
        "targetConceptDomain": "",
        "targetConceptSubDomain": "",
        "sourceFrame": "",
        "targetFrame": ""
    }
    if not lcc_annotation:
        output["sid"] = sid

    best_cm = ""
    bestlink = 0

    CMs = {}

    for target_s in target_strucs:
        t_v = collect_vars(target_strucs, target_s, equalities)
        t_domains = set()

        for targ in target_strucs[target_s]:
            if len(target_strucs[target_s][targ]) == 0 and \
               (target_s, target_s) not in t_domains:
                t_domains.add((target_s, target_s))
            else:
                for (tsubd, tsubarg) in target_strucs[target_s][targ]:
                    if (target_s, tsubd) not in t_domains:
                        t_domains.add((target_s, tsubd))

        s_domains = set()
        for source_s in source_strucs:
            for sarg in source_strucs[source_s]:
                for (ssub_s, ssarg) in source_strucs[source_s][sarg]:
                    sargs = [ssarg]
                    sargs += equalities[ssarg].keys()
                    link = -1
                    print(source_s, ssub_s, sargs)
                    link = test(set(t_v), set(sargs), equalities, other_args)
                    print(link)
                    s_domains.add((source_s, ssub_s, (1 - 0.05 - 0.1 * link)))

                    # for domain in targets:
                    for (t, ts) in t_domains:
                        domain = t
                        for (s, ss, c) in s_domains:
                            ts_pair = "%s,%s,%s,%s,%s" % (domain, t, ts, s, ss)
                            if ts_pair in CMs:
                                if CMs[ts_pair] < c:
                                    CMs[ts_pair] = c
                            else:
                                CMs[ts_pair] = c

                            if c > bestlink:
                                bestlink = c
                                best_cm = "%s,%s,%s,%s,%s" % (domain, t, ts, s, ss)

    explanation_appendix = "\n%%BEGIN_CM_LIST\n"
    for ts_pair in CMs.keys():
        parts = ts_pair.split(",")
        explanation_appendix += "%s,%s,%s,%s,%s,%s\n" \
                               % (parts[1], parts[1], parts[1], parts[3],
                                  parts[3], CMs[ts_pair])
    explanation_appendix += "%%END_CM_LIST"
    output["isiAbductiveExplanation"] += explanation_appendix.encode("utf-8")

    data = best_cm.split(",")
    l = len(data)
    if l > 0:
        output["targetConceptDomain"] = data[0]
    if l > 1:
        output["targetConceptSubDomain"] = data[1]
    if l > 2:
        output["targetFrame"] = data[2]
    if l > 3:
        output["sourceFrame"] = data[3]
    if l > 4:
        output["sourceConceptSubDomain"] = data[4]

    return output
