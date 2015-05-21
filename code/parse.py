import subprocess
import xml.etree.ElementTree as ET
import numpy as np
import os


class Trace():
    """ This class represents a trace of (x,y) coordinates within a single symbol """

    def __init__(self, tid, point_list):
        self.id = tid
        tempx = []
        tempy = []
        xy = point_list.split(',')
        for xy_point in xy:
            tempx.append(xy_point.lstrip().split()[0])
            tempy.append(xy_point.lstrip().split()[1])
        self.x = list(map(float, tempx))
        self.y = list(map(float, tempy))

    def get_boundaries(self):
        x = np.asarray(self.x)
        y = np.asarray(self.y)
        return np.amin(x), np.amax(x), np.amin(y), np.amax(y)


class Symbol():
    """ This class represents a single Symbol to be classified """

    def __init__(self, num_in_inkml, label, labelXML, label_index, trace_list):
        self.label = label
        self.labelXML = labelXML
        self.label_index = label_index
        self.trace_list = trace_list
        self.num_in_inkml = num_in_inkml
        
        x, y = self.get_all_points()
        self.minx = min(x)
        self.maxx = max(x)
        self.centerx = min(x) + (max(x) - min(x))/2
        self.miny = min(y)
        self.maxy = max(y)
        self.centery = min(y) + (max(y) - min(y))/2
        
    def get_all_points(self):
        xtemp = []
        ytemp = []
        for trace in self.trace_list:
            xtemp.extend(trace.x)
            ytemp.extend(trace.y)
        return xtemp, ytemp


class InkmlFile():
    """ This class represents the data from a single input InkML file """

    def __init__(self, label, fname, symbol_list, auto_segment=False):
        self.label = label
        self.fname = self.get_fname(fname)
        self.symbol_list = symbol_list
        self.class_decisions = [0]*len(symbol_list)
        self.relations = None
        # call the crohmeToLg tool in order to get the relationship info
        if auto_segment:
            try:
                perl_out = subprocess.check_output(["perl", "crohme2lg.pl", "-s", fname])
                # decode the binary that is returned into a string
                string_out = perl_out.decode("utf-8")
                self.relations = string_out[string_out.index("# Relations"):]
            except Exception as e:
                print("Issue with processing", fname, "into .lg:", e)

    def get_trace_list(self):
        all_trace_list = []
        for symbol in self.symbol_list:
            for trace in symbol.trace_list:
                all_trace_list.append(trace)
        #need to sort trace by tid to revert to original inkml ordering
        all_trace_list.sort(key=lambda x: int(x.id), reverse=True)
        return all_trace_list

    @staticmethod
    def get_fname(fname):
        """ Returns the name only of a file without path or file extension """
        base = os.path.basename(fname)
        return os.path.splitext(base)[0]

    def print_gt(self, directory, relations):
        """ this prints the ground truth classification and segmentation with our relations """
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, self.fname + ".lg"), "w") as f:
            f.write("# " + self.label + " (Object format)\n")
            f.write("# " + str(len(self.symbol_list)) + " objects (symbols)\n")
            f.write("# FORMAT:\n")
            f.write("# O, Object ID, Label, Weight, List of Primitive IDs (strokes in a symbol)\n")
            for i in range(len(self.symbol_list)):
                strokes = ""
                for trace in self.symbol_list[i].trace_list:
                    strokes += str(trace.id) + ", "
                strokes = strokes[:-2]  # cut off the last comma
                f.write("O, " + self.symbol_list[i].labelXML + ", " + self.symbol_list[i].label +
                        ", 1.0, " + strokes + "\n")
            # now the relations
            f.write("# Relations from SRT:\n")
            for line in relations:
                f.write("EO, " + line[0] + ", " + line[1] + ", " + line[2] + ", 1.0\n")

    def print_it(self, directory, grammar_inv, symbol_list=None):
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, self.fname + ".lg"), "w") as f:
            f.write("# " + self.label + " (Object format)\n")
            f.write("# " + str(len(self.symbol_list)) + " objects (symbols)\n")
            f.write("# FORMAT:\n")
            f.write("# O, Object ID, Label, Weight, List of Primitive IDs (strokes in a symbol)\n")
            if symbol_list is None:  # use ground truth symbols for classification testing
                for i in range(len(self.symbol_list)):
                    strokes = ""
                    for trace in self.symbol_list[i].trace_list:
                        strokes += str(trace.id) + ", "
                    strokes = strokes[:-2]  # cut off the last comma
                    f.write("O, " + self.symbol_list[i].labelXML + ", " + grammar_inv[self.class_decisions[i]] +
                            ", 1.0, " + strokes + "\n")
                if self.relations is not None:
                    f.write("\n" + self.relations)
            else:  # the model is responsible for segmentation here
                labels = {}  # for the labels keep a hash of what you have seen before to number them
                for i in range(len(symbol_list)):  # symbol_list is [(class, [traceIDs])]
                    class_decision = grammar_inv[symbol_list[i][0]]
                    if class_decision in labels:
                        labels[class_decision] += 1
                        label = class_decision + "_" + str(labels[class_decision])
                    else:
                        labels[class_decision] = 1
                        label = class_decision + "_1"
                    strokes = ""
                    for trace in symbol_list[i][1]:
                        strokes += str(trace) + ", "
                    strokes = strokes[:-2]  # cut off the last comma
                    f.write("O, " + label + ", " + class_decision + ", 1.0, " + strokes + "\n")
                if self.relations is not None:
                    f.write("\n" + self.relations)


class Grammar():

    def __init__(self, grammar_file):
        self.grammar = {}
        self.grammar_inv = {}
        try:
            i = 0
            with open(grammar_file) as f:
                for line in f:
                    sym = line.strip()
                    if sym != ",":
                        self.grammar[sym] = i
                        self.grammar_inv[i] = sym
                    else:
                        self.grammar["COMMA"] = i
                        self.grammar_inv[i] = "COMMA"
                    i += 1
        except IOError:
            print("Error: no grammar or symbol list found. Please ensure you have listSymbolsPart4-revised.txt"
                  " in the current directory or have specified a different symbol list")
            raise


class Parser():
    """ This class reads the grammar file and parses the input files """

    def __init__(self):
        """
        Initializes the parser for the Inkml files
        """
        self.parsed_inkml = []

    def parse(self, filelist, grammar):
        """
        Walks the XML tree and parses each XML file
        and saves results into self.parsed_inkml
        :param filelist: the files to parse as a list of Strings
        :param grammar: the symbols used as output classes
        """
        ns = {'inkml': 'http://www.w3.org/2003/InkML'}
        inkmlfilelist = []

        for filename in filelist:
            print("parsing", filename)
            num_in_inkml = 0
            with open(filename, 'r') as filexml:
                tree = ET.parse(filexml)
            root = tree.getroot()
            # get all traces for eqn
            tracelisttemp = {}
            for trace in root.findall('inkml:trace', ns):
                traceid = int(trace.attrib['id'])
                #generate list of (x,y)
                tracelisttemp[traceid] = Trace(traceid, trace.text)
            #get all symbols
            symbollist = []
            toptracegroup = root.find('inkml:traceGroup', ns)
            for subTraceGroup in toptracegroup.findall('inkml:traceGroup', ns):  # for each symbol
                try:
                    annotationXMLelement = subTraceGroup.find('inkml:annotationXML', ns)
                    if annotationXMLelement is None or annotationXMLelement.attrib['href'] is None:
                        annotationXML = "No_Label"
                    else:
                        annotationXML = annotationXMLelement.attrib['href']
                except Exception as e:
                    print("Error in", filename, ":", e)
                    exit()
                annotation = subTraceGroup.find('inkml:annotation', ns).text
                if annotation is None:
                    annotation = "No_Label"
                #get tracelist for symbol
                traceviewlisttemp = []
                for traceview in subTraceGroup.findall('inkml:traceView', ns):
                    tid = int(traceview.attrib['traceDataRef'])
                    traceviewlisttemp.append(tid)
                tracelist = [tracelisttemp[k] for k in traceviewlisttemp]  # trace subset for symbol
                # find what index this symbol corresponds to
                if annotation == ",":
                    annotation = "COMMA"
                if annotationXML[0:2] == ",_":
                    annotationXML = "COMMA" + annotationXML[1:]
                assert annotation in grammar, "Error: " + annotation + " is not defined in the grammar"
                label_index = grammar[annotation]
                symbollist.append(Symbol(num_in_inkml, annotation, annotationXML, label_index, tracelist))
                num_in_inkml += 1
            #generate class for equation
            label = ""
            for annotation in root.findall('inkml:annotation', ns):
                if annotation.attrib['type'] == 'truth':
                    label = annotation.text
            # create the inkml class to hold the data
            inkmlfilelist.append(InkmlFile(label, filename, symbollist))
        # store the results
        self.parsed_inkml = inkmlfilelist

    def print_results(self, traces=False):
        """ Prints all of the files parsed by the system """
        for file in self.parsed_inkml:
            print("file:", file.label, "filename", file.fname)
            for symbol in file.symbol_list:
                print('\t', "symbol:", symbol.label, "index:", symbol.label_index)
                if traces:
                    for trace in symbol.trace_list:
                        print('\t\t', "trace:", str(trace.id))
                        print(trace.x)
                        print(trace.y)
            print()