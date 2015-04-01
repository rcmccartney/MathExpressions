import xml.etree.ElementTree as ET
import os
import pickle
from collections import defaultdict

path = 'C:\\Users\\Jie\\Desktop\\Misc_RIT_documents\\PatternRecognition\\TrainINKML_v3\\extension\\test'

#{symbol: list of instances}
#each instance is {1:[x,y,x,y], 2:[x,y,x,y], 5:[x,y,x,y]}
#since the whole equation is lost, trace number is ordinal only
symbolList = defaultdict(list)
ns = {'inkml': 'http://www.w3.org/2003/InkML'}
for filename in os.listdir(path):
	fullname = os.path.join(path, filename)
	tree = ET.parse(fullname)
	root = tree.getroot()
	
	#store trace strokes in list
	'''traceList = []
	for trace in root.findall('inkml:trace',ns):
		traceIndex = int(trace.attrib['id'])
		traceVals = trace.text.replace(',','').replace(' ',',')
		traceValSplit = traceVals.split(',')
		x=[]
		y=[]
		for i in range(0,len(traceValSplit)):
			if i % 2 == 0:
				x.append(int(traceValSplit[i]))
			else:
				y.append(int(traceValSplit[i]))
		traceList.insert(traceIndex,[x, y])
	print(traceList)'''
	
	
	#parse traceGroups, one instance
	'''for topTraceGroup in root.findall('inkml:traceGroup',ns):
		for subTraceGroup in topTraceGroup.findall('inkml:traceGroup',ns):
			subTraceGroupList = []
			for traceStroke in subTraceGroup.findall('inkml:traceView',ns):
				subTraceGroupList.append(int(traceStroke.attrib['traceDataRef']))
			traceGroupList.append(subTraceGroupList)
	print(traceGroupList)'''
	
	
	#extract individual symbols
	for topTraceGroup in root.findall('inkml:traceGroup',ns):
		for subTraceGroup in topTraceGroup.findall('inkml:traceGroup',ns):
			truthSymbol = "" #will store the true annotation
			symbolTraces = {}
			for annotation in subTraceGroup.findall('inkml:annotation',ns):
				truthSymbol = annotation.text
			for traceView in subTraceGroup.findall('inkml:traceView',ns):
				traceNum = int(traceView.attrib['traceDataRef'])
				for trace in root.findall('inkml:trace',ns):
					traceId = int(trace.attrib['id'])
					if traceId == traceNum:
						symbolTraces[traceId] = trace.text.replace('\n','').replace(',','').replace(' ',',')
			symbolList[truthSymbol].append(symbolTraces)
			
#pickle.dump(symbolList, open("symbolList.p","wb"))
for a in symbolList:
	print(a)
	print(symbolList[a])
	print('')
	print('')