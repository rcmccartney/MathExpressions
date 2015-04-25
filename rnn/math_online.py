#!/usr/bin/env python
import pickle
from parse import Parser, InkmlFile, Symbol, Trace 
import netcdf_helpers
from scipy import *
from optparse import OptionParser
import sys
import os
from xml.dom.minidom import parse

#inputMeans = array([511.8343, 102.7592, 0.03199977])
#inputStds = array([134.0498, 24.34094, 0.1758981])

#command line options
parser = OptionParser()

#parse command line options
(options, args) = parser.parse_args()
if (len(args)<2):
	print "usage: -options input_filename output_filename"
	print options
	sys.exit(2)

inputFilename = args [0]
ncFilename = args[1]
print options
print "input filename", inputFilename
print "data filename", ncFilename
seqDims = []
seqLengths = []
targetStrings = []
wordTargetStrings = []
seqTags = []
inputs = []

with open(os.path.relpath("parsed.pkl"), 'rb') as handle:
	p = pickle.load(handle)
labels = ["*"]
for l in p.grammar:
	if l == ",":
		labels.append('COMMA')
	else:
		labels.append(l)

print "reading data files"
for inkml in p.parsed_inkml:
	seqTags.append(inkml.fname)
	word = ""
	ts = ""
	for s in inkml.symbol_list:
		label = s.label if s.label != "," else "COMMA"
		word += "*" + label.strip()
		ts += label.strip() + ' '
	print word
	wordTargetStrings.append(word)
	print ts
	targetStrings.append(ts.strip())
	oldlen = len(inputs)
	for s in inkml.symbol_list:
		for t in s.trace_list:
			for i in range(len(t.x)):
				inputs.append([t.x[i], 
					       t.y[i], 
					       0.0])
			inputs[-1][-1] = 1
	seqLengths.append(len(inputs) - oldlen)
	seqDims.append([seqLengths[-1]])

#inputs = ((array(inputs)-inputMeans)/inputStds).tolist()
print len(labels), labels
print labels

#create a new .nc file
file = netcdf_helpers.NetCDFFile(ncFilename, 'w')

#create the dimensions
netcdf_helpers.createNcDim(file,'numSeqs',len(seqLengths))
netcdf_helpers.createNcDim(file,'numTimesteps',len(inputs))
netcdf_helpers.createNcDim(file,'inputPattSize',len(inputs[0]))
netcdf_helpers.createNcDim(file,'numDims',1)
netcdf_helpers.createNcDim(file,'numLabels',len(labels))

#create the variables
netcdf_helpers.createNcStrings(file,'seqTags',seqTags,('numSeqs','maxSeqTagLength'),'sequence tags')
netcdf_helpers.createNcStrings(file,'labels',labels,('numLabels','maxLabelLength'),'labels')
netcdf_helpers.createNcStrings(file,'targetStrings',targetStrings,('numSeqs','maxTargStringLength'),'target strings')
netcdf_helpers.createNcStrings(file,'wordTargetStrings',wordTargetStrings,('numSeqs','maxWordTargStringLength'),'word target strings')
netcdf_helpers.createNcVar(file,'seqLengths',seqLengths,'i',('numSeqs',),'sequence lengths')
netcdf_helpers.createNcVar(file,'seqDims',seqDims,'i',('numSeqs','numDims'),'sequence dimensions')
netcdf_helpers.createNcVar(file,'inputs',inputs,'f',('numTimesteps','inputPattSize'),'input patterns')

#write the data to disk
print "closing file", ncFilename
file.close()
