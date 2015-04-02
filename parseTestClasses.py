import xml.etree.ElementTree as ET
import os
import sys
import ntpath
from split import *


class Trace():

    def __init__(self, id, point_list):
        self.id = id
        xy = point_list.split(',')
        xy = list(map(float, xy))
        self.x = xy[::2]
        self.y = xy[1::2]


class Symbol():

    def __init__(self, label, label_index, trace_list):
        self.label = label
        self.label_index = label_index
        self.traceList = trace_list


class InkmlFile():

    def __init__(self, label, fname, symbol_list):
        self.label = label
        self.fname = fname
        self.symbolList = symbol_list


class Parser():

    def __init__(self):
        self.grammar = {}
        self.parsed_inkml = []
        try:
            i = 0
            for line in open("listSymbolsPart4-revised.txt"):
                self.grammar[line.strip()] = i
                i += 1
        except IOError:
            print("Error: no grammar or symbol list found. Please ensure you "
                  "have listSymbolsPart4-revised.txt in the current directory")
            raise

    def parse(self, filelist):

        ns = {'inkml': 'http://www.w3.org/2003/InkML'}
        inkmlfilelist = []

        for filename in filelist:
            with open(filename, 'r') as filexml:
                tree = ET.parse(filexml)
            root = tree.getroot()

            #get all traces for eqn
            tracelisttemp = {}
            for trace in root.findall('inkml:trace', ns):
                traceid = int(trace.attrib['id'])
                #generate list of (x,y)
                traceval = trace.text.replace('\n', '').replace(',', '').replace(' ', ',')
                tracelisttemp[traceid] = Trace(traceid, traceval)

            #get all symbols
            symbollist = []
            toptracegroup = root.find('inkml:traceGroup', ns)
            for subTraceGroup in toptracegroup.findall('inkml:traceGroup', ns):  # for each symbol
                annotation = subTraceGroup.find('inkml:annotation', ns).text
                #get tracelist for symbol
                traceviewlisttemp = []
                for traceview in subTraceGroup.findall('inkml:traceView', ns):
                    id = int(traceview.attrib['traceDataRef'])
                    traceviewlisttemp.append(id)
                tracelist = [tracelisttemp[k] for k in traceviewlisttemp]  # trace subset for symbol
                # find what index this symbol corresponds to
                assert annotation in self.grammar, "Error: " + annotation + " is not defined in the grammar"
                label_index = self.grammar[annotation]
                symbollist.append(Symbol(annotation, label_index, tracelist))

            #generate class for equation
            label = ""
            for annotation in root.findall('inkml:annotation', ns):
                if annotation.attrib['type'] == 'truth':
                    label = annotation.text

            # get just the last part of the path for the filename
            head, tail = ntpath.split(filename)
            fname = tail or ntpath.basename(head)
            inkmlfilelist.append(InkmlFile(label, fname.strip(".inkml"), symbollist))
        # store the results
        self.parsed_inkml = inkmlfilelist

    def print_results(self):
        for file in self.parsed_inkml:
            print("file:", file.label, "filename", file.fname)
            for symbol in file.symbolList:
                print('\t', "symbol:", symbol.label, "index:", symbol.label_index)
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

    p = Parser()
    if len(sys.argv) < 3:
        print_usage()
    elif sys.argv[1] == "-f":  # operate on files
        p.parse(sys.argv[2:])
    elif sys.argv[1] == "-d":  # operate on directories
        filelist = []
        for arg in sys.argv[2:]:
            for filename in os.listdir(arg):
                filelist.append(os.path.join(arg, filename))
        p.parse(filelist)
    elif sys.argv[1] == "-l":  # operate on a filelist
        f = open(sys.argv[2])
        p.parse(f.readlines())
        f.close()
    else:
        print_usage()

    p.print_results()
    s = Split(p.parsed_inkml, len(p.grammar))
    s.optimize_cosine()

if __name__ == '__main__':
    main()