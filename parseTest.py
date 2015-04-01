import xml.etree.ElementTree as ET
import os

path = 'C:\\Users\\Jie\\Desktop\\Misc_RIT_documents\\PatternRecognition\\TrainINKML_v3\\extension\\test'

for filename in os.listdir(path):
	fullname = os.path.join(path, filename)
	tree = ET.parse(fullname)
	root = tree.getroot()
	
	#for child in root:
	#	print(child.tag)
	for topTraceGroup in root.findall('{http://www.w3.org/2003/InkML}traceGroup'):
		for subTraceGroup in topTraceGroup.findall('{http://www.w3.org/2003/InkML}traceGroup'):
			print(subTraceGroup.tag)
	