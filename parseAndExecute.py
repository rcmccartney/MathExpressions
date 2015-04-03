import xml.etree.ElementTree as ET
import os
import sys
import ntpath
from split import *
from features import *
from classifier import *

class Trace():
    """ This class represents a trace of (x,y) coordinates within a single symbol """

    def __init__(self, id, point_list):
        self.id = id
        xy = point_list.split(',')
        xy = list(map(float, xy))
        self.x = xy[::2]
        self.y = xy[1::2]


class Symbol():
    """ This class represents a single Symbol to be classified """

    def __init__(self, label, label_index, trace_list):
        self.label = label
        self.label_index = label_index
        self.trace_list = trace_list


class InkmlFile():
    """ This class represents the data from a single input InkML file """

    def __init__(self, label, fname, symbol_list):
        self.label = label
        self.fname = fname
        self.symbol_list = symbol_list


class Parser():
    """ This class reads the grammar file and parses the input files """

    def __init__(self, grammar_file):
        """
        Initializes the parser for the Inkml files
        :param grammar_file: file containing the valid symbols to be classified
        """
        self.grammar = {}
        self.parsed_inkml = []
        try:
            i = 0
            for line in open(grammar_file):
                self.grammar[line.strip()] = i
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
            with open(filename, 'r') as filexml:
                tree = ET.parse(filexml)
            root = tree.getroot()

            # get all traces for eqn
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


def print_usage():
    """ Prints correct usage of the program and exits """

    print("$ python3 parseInkml [flag] [arguments]")
    print("flags:")
    print("  -t <params.txt>     : train classifier with optional output file (no flag set will perform testing)")
    print("  -p [params.txt]     : load parameters for testing from params.txt instead of default location")
    print("  -d [dir1 dir2...]   : operate on the specified directories")
    print("  -f [file1 file2...] : operate on the specified files")
    print("  -l [filelist.txt]   : operate on the files listed in the specified text file")
    print("  -v                  : turn on verbose output")
    sys.exit(1)


def main():
    """
    This is the pipeline of the system
    """
    if len(sys.argv) < 3:
        print_usage()

    testing = True
    verbose = False
    default_out = "params.txt"
    # :TODO allow grammar to be taken on command line
    # :TODO JIE make sure the above works for the time data
    # :TODO JIE make sure the above works when the testing class is missing
    grammar_file = "listSymbolsPart4-revised.txt"

    print("Running", sys.argv[0])
    if "-v" in sys.argv:
        print("-v : using verbose output")
        verbose = True
        sys.argv.remove("-v")

    if "-t" in sys.argv:
        index = sys.argv.index("-t")
        if index < len(sys.argv) - 1 and "-" not in sys.argv[index+1]:
            default_out = sys.argv[index+1]
            sys.argv.remove(default_out)
        sys.argv.remove("-t")
        testing = False
        print("-t : training the classifier from parameters saved in", default_out)
    else:
        if "-p" in sys.argv:
            i = sys.argv.index("-p")
            default_out = sys.argv[i + 1]
            sys.argv.remove("-p")
            sys.argv.remove(default_out)
            print("-p set,", end=" ")
        print("-t not set : testing the classifier from parameters saved in", default_out)

    # STEP 1 - PARSING
    print("\n############ Parsing input data ############")
    p = Parser(grammar_file)
    if sys.argv[1] == "-f":  # operate on files
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
    print("Parsed", len(p.parsed_inkml), "InkML files")
    if verbose:
        p.print_results()

    # STEP 2 - SPLITTING (ONLY FOR TRAINING) AND
    # STEP 3 - FEATURE EXTRACTION
    if not testing:
        print("\n########### Splitting input data ###########")
        s = Split(p.parsed_inkml, p.grammar, verbose)
        s.optimize_cosine()
        print("\n######## Running feature extraction ########")
        f = FeatureExtraction(s.train, s.test, verbose)
    else:
        print("\n######## Running feature extraction ########")
        f = FeatureExtraction(p.parsed_inkml, None, verbose)

    # STEP 4 - CLASSIFICATION
    c = Classifier(f.get_fake_data()[0], f.get_fake_data()[1], default_out, testing, verbose)
    if not testing:
        print("\n########## Training the classifier #########")

    print("\n########## Running classification ##########")


if __name__ == '__main__':
    main()