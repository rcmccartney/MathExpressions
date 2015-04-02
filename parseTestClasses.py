import xml.etree.ElementTree as ET
import os
import sys


class Trace():
    def __init__(self, id, pointList):
        self.id = id
        xy = pointList.split(',')
        self.x = xy[::2]
        self.y = xy[1::2]


class Symbol():
    def __init__(self, label, traceList):
        self.label = label
        self.traceList = traceList


class InkmlFile():
    def __init__(self, label, symbolList):
        self.label = label
        self.symbolList = symbolList


def parse(filelist):

    ns = {'inkml': 'http://www.w3.org/2003/InkML'}
    inkmlFileList = []

    for filename in filelist:
        tree = ET.parse(filename)
        root = tree.getroot()

        #get all traces for eqn
        traceListTemp = {}
        for trace in root.findall('inkml:trace', ns):
            traceId = int(trace.attrib['id'])
            #generate list of (x,y)
            traceVal = trace.text.replace('\n', '').replace(',', '').replace(' ', ',')
            traceListTemp[traceId] = Trace(traceId, traceVal)

        #get all symbols
        symbolList = []
        topTraceGroup = root.find('inkml:traceGroup', ns)
        for subTraceGroup in topTraceGroup.findall('inkml:traceGroup', ns):  # for each symbol
            annotation = subTraceGroup.find('inkml:annotation', ns).text
            #get traceList for symbol
            traceViewListTemp = []
            for traceView in subTraceGroup.findall('inkml:traceView', ns):
                id = int(traceView.attrib['traceDataRef'])
                traceViewListTemp.append(id)
            traceList = [traceListTemp[k] for k in traceViewListTemp]  # trace subset for symbol

            symbolList.append(Symbol(annotation, traceList))

        #generate class for equation
        for annotation in root.findall('inkml:annotation', ns):
            if annotation.attrib['type'] == 'truth':
                label = annotation.text
        inkmlFileList.append(InkmlFile(label, symbolList))

    for file in inkmlFileList:
        print("file:", file.label)
        for symbol in file.symbolList:
            print('\t', "symbol:", symbol.label)
            for trace in symbol.traceList:
                print('\t\t', "trace:", str(trace.id))
                print(trace.x)
                print(trace.y)
        print()


def print_usage():
    print("$ python3 parseInkml [flag] [arguments]")
    print("flags:")
    print("  -d [dir1 dir2...]   : operate on specified directories")
    print("  -f [file1 file2...] : operate on the specified files")
    print("  -l [filelist.txt]   : operate on the files in the specified text file")


def main():
    if len(sys.argv) < 3:
        print_usage()
    elif sys.argv[1] == "-f":  # operate on files
        parse(sys.argv[2:])
    elif sys.argv[1] == "-d":  # operate on directories
        filelist = []
        for arg in sys.argv[2:]:
            for filename in os.listdir(arg):
                filelist.append(os.path.join(arg, filename))
        print(filelist)
        parse(filelist)
    elif sys.argv[1] == "-l":  # operate on a filelist
        f = open(sys.argv[2])
        parse(f.readlines())
        f.close()
    else:
        print_usage()


if __name__ == '__main__':
    main()