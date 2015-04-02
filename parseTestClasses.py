import xml.etree.ElementTree as ET
import os
import pickle
from collections import defaultdict

path = 'C:\\Users\\Jie\\Desktop\\Misc_RIT_documents\\PatternRecognition\\TrainINKML_v3\\extension\\test'


class Trace:
    def __init__(self, id, pointList):
        self.id = id
        '''self.points = []
        xy = pointList.split(',')
        traceValList = []
        for i in range(0,len(xy),2):
            self.points.append((int(xy[i]),int(xy[i+1])))'''
        xy = pointList.split(',')
        self.x = xy[::2]
        self.y = xy[1::2]

class Symbol:
    def __init__(self, label, traceList):
        self.label = label
        self.traceList = traceList
        
class InkmlFile:

    def __init__(self, label, symbolList):
        self.label = label
        self.symbolList = symbolList

ns = {'inkml': 'http://www.w3.org/2003/InkML'}
inkmlFileList = []
for filename in os.listdir(path):
    fullname = os.path.join(path, filename)
    tree = ET.parse(fullname)
    root = tree.getroot()

    #get all traces for eqn
    traceListTemp = {}
    for trace in root.findall('inkml:trace',ns):
        traceId = int(trace.attrib['id'])
        #generate list of (x,y)
        traceVal = trace.text.replace('\n','').replace(',','').replace(' ',',')
        traceListTemp[traceId] = Trace(traceId,traceVal)

    #get all symbols
    symbolList = []
    topTraceGroup = root.find('inkml:traceGroup',ns)
    for subTraceGroup in topTraceGroup.findall('inkml:traceGroup',ns): #for each symbol
        annotation = subTraceGroup.find('inkml:annotation',ns).text
        #get traceList for symbol
        traceViewListTemp = []
        for traceView in subTraceGroup.findall('inkml:traceView',ns):
            id = int(traceView.attrib['traceDataRef'])
            traceViewListTemp.append(id)
        traceList = [traceListTemp[k] for k in traceViewListTemp] #trace subset for symbol
        
        symbolList.append(Symbol(annotation,traceList))
        
    #generate class for equation
    for annotation in root.findall('inkml:annotation',ns):
        if annotation.attrib['type'] == 'truth':
            label = annotation.text
    inkmlFileList.append(InkmlFile(label,symbolList))


for file in inkmlFileList:
    print(file.label)
    for symbol in file.symbolList:
        print('\t' + symbol.label)
        for trace in symbol.traceList:
            print('\t\t' + str(trace.id))
            print(trace.x)
            print(trace.y)
    print('')