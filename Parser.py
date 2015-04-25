import subprocess
import xml.etree.ElementTree as ET
from features import *
from classifier import *


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
        if label != ",":
            self.label = label
        else:
            self.label = "COMMA"
        if labelXML[0:2] != ",_":
            self.labelXML = labelXML
        else:
            self.labelXML = "COMMA" + labelXML[1:]
        self.label_index = label_index
        self.trace_list = trace_list
        self.num_in_inkml = num_in_inkml

    def print_traces(self):
        FeatureExtraction.convert_and_plot(self.trace_list)

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
        # call the crohmeToLg tool in order to get the relationship info
        if auto_segment:
            try:
                self.relations = None
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

    def print_it(self, directory, grammar_inv):
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
                f.write("O, " + self.symbol_list[i].labelXML + ", " + grammar_inv[self.class_decisions[i]] +
                        ", 1.0, " + strokes + "\n")
            if self.relations is not None:
                f.write("\n" + self.relations)


class Parser():
    """ This class reads the grammar file and parses the input files """

    def __init__(self, verbose, grammar_file):
        """
        Initializes the parser for the Inkml files
        :param grammar_file: file containing the valid symbols to be classified
        """
        self.verbose = verbose
        self.grammar = {}
        self.grammar_inv = {}
        self.parsed_inkml = []
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

    def parse(self, filelist):
        """
        Walks the XML tree and parses each XML file
        and saves results into self.parsed_inkml
        :param filelist: the files to parse as a list of Strings
        """
        ns = {'inkml': 'http://www.w3.org/2003/InkML'}
        inkmlfilelist = []

        for filename in filelist:
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
                    annotationXMLelement = subTraceGroup.find('inkml:annotationXML',ns)
                    if annotationXMLelement is None or annotationXMLelement.attrib['href'] is None:
                        annotationXML = "No_Label"
                    else:
                        annotationXML = annotationXMLelement.attrib['href']

                except:
                    print("Error in", filename)
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
                assert annotation in self.grammar, "Error: " + annotation + " is not defined in the grammar"
                label_index = self.grammar[annotation]
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

    def print_results(self):
        """ Prints all of the files parsed by the system """
        for file in self.parsed_inkml:
            print("file:", file.label, "filename", file.fname)
            for symbol in file.symbol_list:
                print('\t', "symbol:", symbol.label, "index:", symbol.label_index)
                for trace in symbol.trace_list:
                    print('\t\t', "trace:", str(trace.id))
                    print(trace.x)
                    print(trace.y)
            print()