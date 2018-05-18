#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from __future__ import print_function

import re
import json
import sys
from sets import Set
from collections import defaultdict

def printerr(*objs):
    print("", *objs, file=sys.stderr)
	
#computes the transitive closure of an hash in which links are represented by 
def transitive_closure(A):
	while True:
		newlink = False

		newA = defaultdict(dict)
		for x in A.keys():
			for y in A[x].keys():
				for z in A[y].keys():
					if x!=z and not A[x].has_key(z):
						newA[x][z]=1
						newA[z][x]=1
						newlink = True

		if newlink:
			for x in newA.keys():
				for y in newA[x].keys():
					A[x][y]=1
		else:
			break

	return A

# find index of SubStr in MainStr
def findIndexes(SubStr,MainStr):
	if len(SubStr)==0: return []

	inds = []
	ss_toks=nltk.word_tokenize(SubStr.rstrip().lower())
	ms_toks=nltk.word_tokenize(MainStr.rstrip().lower())

	#print ss_toks
	#print ms_toks

	for mi, mt in enumerate(ms_toks):
		if ss_toks[0] == mt and len(ms_toks)>=mi+len(ss_toks)-1:
			inds.append(mi)
			found = True
			if len(ss_toks)>1:
				for si in range(1,len(ss_toks)):
					if ss_toks[si] != ms_toks[mi+si]:
						found = False
						break
					else:
						inds.append(mi+si)
			if found:
				#print inds
				return inds
			else:
				inds = []

	return inds

#hash with key the domain(subdomain) and value ta list of list of arguments
#output <domain,<domain_arg,((subdomain,subdomain_arg)...)>>
def createDStruc(superD,subD):
	outputstrucs = defaultdict(dict)

	for superd in superD:
		for superArgs in superD[superd]:
			if (not outputstrucs.has_key(superd) or not outputstrucs[superd].has_key(superArgs[0])): outputstrucs[superd][superArgs[0]] = []

			if subD:
				for subd in subD:
					for subArgs in subD[subd]:
						if len(subArgs)>1 and superArgs[0]==subArgs[1]:
							outputstrucs[superd][superArgs[0]].append((subd,subArgs[0]))
			else:
				outputstrucs[superd][superArgs[0]].append(('',superArgs[0]))
	return outputstrucs

#returns the list of variables in the target-subtarget pair
def collectVars(struc,superkey,equalities):
	output = []

	for arg in struc[superkey]:
		if not arg.startswith('_') and not arg in output:
			output.append(arg)
			if equalities.has_key(arg):
				for a in equalities[arg]: output.append(a)
		for (subd,subarg) in struc[superkey][arg]:
			if not subarg.startswith('_') and not subarg in output:
				output.append(subarg)
				if equalities.has_key(subarg):
					for a in equalities[subarg]: output.append(a)
	return output

# given two sets of arguments and the equalities
# return the minimum distance between any of the variables in the two sets.
# s_all: all the variables visited till now
# s_end: second set increased by equalities
# s_current: current set of variables
# s_current:=first set
# increase s_current with equalities
# if s_current contains one variable of s_end terminate and return current path length.
#  find all predications that use a variable of s_current, get the other arguments
#  remove from the other variables the variable already in s_current
#  add the remaining to the s_new set
# increase current path length
# loop using s_new as s_current
# terminate if after 9 iterations the s_end has not been reached or if s_new is empty. (return in both cases the max of 9)
def test(vs1,vsend,equalities,otherVars,pathlength=0):
	if not vs1 or not vsend: return 9
	if pathlength>=9:
		return pathlength
	for x in vs1:
		if x in equalities:
			vs1.union(equalities[x].keys())
	if any(x in vs1 for x in vsend):
		return pathlength
	pathlength+=1
	vs1New=Set()
	for x in vs1:
		if x in otherVars:
			vs1New.update(otherVars[x])
	for x in vs1:
		if x in vs1New:
			vs1New.remove(x)
	return test(vs1New,vsend,equalities,otherVars,pathlength)
		
def isLinkedbyParse(v1,v2,word_props,equalities,input_been,pathlength):
	if v1==v2: return pathlength

	pathlength += 1
	if pathlength == 9: return pathlength

	been = list(input_been)
	if (v1,v2) in been: return 9
	been.append((v1,v2))
	been.append((v2,v1))

	#print (v1,v2,pathlength)

	#if equalities.has_key(v1) and equalities[v1].has_key(v2): return 2

	nbrs = []
	for (propName,args) in word_props:
		if v1 in args:
			if v2 in args: return pathlength

			for a in args:
				if a!=v1: nbrs.append(a)

	pl = 9
	for n in nbrs:
		npl = isLinkedbyParse(n,v2,word_props,equalities,been,pathlength)
		if npl<pl: pl = npl
	return pl

def extract_CM_mapping(sid,inputString,parse,DESCRIPTION,LCCannotation):
	#LCCannotation: input json request
	#DESCRITION: the description of how to interpret the isi output
	#parse: the parser output?
	#inputString: the abduction output
	targets = dict()
	subtargets = dict()
	subsubtargets = dict()
	sources = dict()
	subsources = dict()
	mappings = dict()
	roles = []
	word_props = []
	equalities = defaultdict(dict)
	otherArgs=defaultdict(Set)

	prop_pattern = re.compile('([^\(]+)\(([^\)]+)\)')
	
	#process the input
	propositions = inputString.split(' ^ ')
	prop_list = []
	for item in propositions:
		prop_match_obj = prop_pattern.match(item)
		if prop_match_obj:
			prop_name = prop_match_obj.group(1)
			arg_str = prop_match_obj.group(2)
			args = arg_str.split(',')

			if prop_name.startswith('T#'):
				dname = prop_name[2:]
				if not targets.has_key(dname): targets[dname] = []
				if args not in targets[dname]: targets[dname].append(args)
			elif prop_name.startswith('TS#'):
				dname = prop_name[3:]
				if not subtargets.has_key(dname): subtargets[dname] = []
				if args not in subtargets[dname]: subtargets[dname].append(args)
			elif prop_name.startswith('TSS#'):
				dname = prop_name[4:]
				if not subsubtargets.has_key(dname): subsubtargets[dname] = []
				if args not in subsubtargets[dname]: subsubtargets[dname].append(args)
			elif prop_name.startswith('S#'):
				dname = prop_name[2:]
				if not sources.has_key(dname): sources[dname] = []
				if args not in sources[dname]: sources[dname].append(args)
			elif prop_name.startswith('SS#'):
				ss_data = prop_name[3:].split('%')
				if len(ss_data)>1: prop_name = ss_data[1]
				else: prop_name = ss_data[0]

				if not subsources.has_key(prop_name): subsources[prop_name] = []
				if args not in subsources[prop_name]:  subsources[prop_name].append(args)
			elif prop_name.startswith('M#'):
				mname = prop_name[2:]
				if not mappings.has_key(mname): mappings[mname] = []
				if args not in mappings[mname]: mappings[mname].append(args)
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
						equalities[arg1][arg2]=1
						equalities[arg2][arg1]=1
						j += 1
			elif prop_name == '!=': continue
			elif prop_name == 'equal':
				equalities[args[1]][args[2]]=1
				equalities[args[2]][args[1]]=1
			else:
				word_props.append((prop_name,args))
				uargs=Set(args)
				for a in uargs:
					otherArgs[a]|=uargs
					

	#print json.dumps(targets, ensure_ascii=False)
	#print json.dumps(subtargets, ensure_ascii=False)
	#print json.dumps(sources, ensure_ascii=False)
	#print json.dumps(subsources, ensure_ascii=False)
	#print json.dumps(word_props, ensure_ascii=False)
	#print json.dumps(mappings, ensure_ascii=False)
	#print(json.dumps(equalities, ensure_ascii=False))

	# transitive closure of equalities
	equalities = transitive_closure(equalities)

	target_strucs = createDStruc(subtargets,subsubtargets)
	source_strucs = createDStruc(sources,subsources)

	#print json.dumps(target_strucs, ensure_ascii=False)
	#print json.dumps(source_strucs, ensure_ascii=False)

	#print json.dumps(equalities, ensure_ascii=False)
	#exit(0)

	output_struct_item = {}
	if not LCCannotation: output_struct_item["sid"] = sid
	output_struct_item["isiDescription"] = DESCRIPTION
	#output_struct_item["targetConceptDomain"] = "ECONOMIC_INEQUALITY"

	bestCM = ''
	bestlink = 0

	Tdomains = []
	Sdomains = []

	CMs = dict()

	for targetS in target_strucs:

		tV = collectVars(target_strucs,targetS,equalities)
		Tdomains = []

		for targ in target_strucs[targetS]:
			if len(target_strucs[targetS][targ])==0 and (targetS,targetS) not in Tdomains:
				Tdomains.append((targetS,targetS))
			else:
				for (tsubd,tsubarg) in target_strucs[targetS][targ]:
					if (targetS,tsubd) not in Tdomains: Tdomains.append((targetS,tsubd))

		#print "Tdomans:"
		#print json.dumps(Tdomains, ensure_ascii=False)
		#print json.dumps(tV, ensure_ascii=False)

		Sdomains = []
		bestSVars = []
		for sourceS in source_strucs:
			for sarg in source_strucs[sourceS]:
				for (ssubS,ssarg) in source_strucs[sourceS][sarg]:
					sargs = [ssarg]
					sargs += equalities[ssarg].keys()
					link = -1
					print (sourceS,ssubS,sargs)
					link=test(Set(tV),Set(sargs),equalities,otherArgs)
					print(link)
					#for tv in tV:
					#	for sv in sargs:
					#		newlink = isLinkedbyParse(tv,sv,word_props,equalities,[],0)
					#		#printerr(targetS,sourceS,ssubS,tv,sv,newlink)
					#		if newlink<link:
					#			link=newlink
					#			if newlink<2:
					#				break
					#	if link<2: break
					Sdomains.append((sourceS,ssubS,(1-0.05-0.1*link)))
					#print "%s,%s,%s" % (sourceS,ssubS,(1-0.05-0.1*link))
					#exit(0)

					#for domain in targets:
					for (t,ts) in Tdomains:
						domain=t
						for (s,ss,c) in Sdomains:
								#explanationAppendix += "ECONOMIC_INEQUALITY,%s,%s,%s,%s,%s\n" % (t,ts,s,ss,c)

								TSpair = "%s,%s,%s,%s,%s" % (domain,t,ts,s,ss)
								if CMs.has_key(TSpair):
									if CMs[TSpair] < c: CMs[TSpair] = c
								else: CMs[TSpair] = c

								if c>bestlink:
									bestlink = c
									bestCM = "%s,%s,%s,%s,%s" % (domain,t,ts,s,ss)

	#print 'BEST: ' + bestCM
	#exit(0)

	explanationAppendix = "\n%%BEGIN_CM_LIST\n"
	for TSpair in CMs.keys():
		parts=TSpair.split(",")
		explanationAppendix += "%s,%s,%s,%s,%s,%s\n" % (parts[1],parts[1],parts[1],parts[3],parts[3],CMs[TSpair])
	explanationAppendix += "%%END_CM_LIST"

	output_struct_item['isiAbductiveExplanation'] = inputString + explanationAppendix.encode("utf-8")
	data = bestCM.split(',')
	l=len(data)
	output_struct_item["targetConceptDomain"] = data[0] if l>0 else ''
	output_struct_item["targetConceptSubDomain"] = data[1] if l>1 else ''
	output_struct_item["targetFrame"] = data[2] if l>2 else ''
	output_struct_item["sourceFrame"] = data[3] if l>3 else ''
	output_struct_item["sourceConceptSubDomain"] = data[4] if l>4 else ''

	#print json.dumps(output_struct_item, ensure_ascii=False)

	return output_struct_item
