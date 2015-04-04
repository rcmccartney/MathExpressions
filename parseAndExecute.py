import xml.etree.ElementTree as ET
import os
import sys
import ntpath
import subprocess
import matplotlib.pyplot as plt
from split import *
from features import *
from classifier import *
from profilehooks17.profilehooks import *


class Trace():
    """ This class represents a trace of (x,y) coordinates within a single symbol """

    def __init__(self, id, point_list):
        self.id = id
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

    def __init__(self, label, labelXML, label_index, trace_list):
        self.label = label
        self.labelXML = labelXML
        self.label_index = label_index
        self.trace_list = trace_list

    def print_traces(self):
        x, y = self.get_all_points()
        plt.figure()
        plt.scatter(x, y)
        plt.pause(3)
        plt.close()
        #rescaled coordinates
        f = FeatureExtraction(None, None, None)
        x_trans, y_trans = f.rescale_points(x, y, 1)
        x_interp, y_interp = f.resample_points(x_trans, y_trans, 5)
        plt.figure()
        plt.scatter(x_trans, y_trans)
        plt.scatter(x_interp, y_interp)
        plt.pause(3)
        plt.close()
    
    def get_all_points(self):
        xtemp = []
        ytemp = []
        for trace in self.trace_list:
            xtemp.extend(trace.x)
            ytemp.extend(trace.y)
        return xtemp, ytemp
    
        
class InkmlFile():
    """ This class represents the data from a single input InkML file """

    def __init__(self, label, fname, symbol_list):
        self.label = label
        self.fname = self.get_fname(fname)
        # call the crohmeToLg tool in order to get the relationship info
        self.symbol_list = symbol_list
        try:
            pass
            #perl_out = subprocess.check_output(["perl", "crohme2lg.pl", "-s", fname])
            # decode the binary that is returned into a string
            #string_out = perl_out.decode("utf-8")
            #self.relations = string_out[string_out.index("# Relations"):]
        except Exception as e:
            print("Issue with processing", fname, "into .lg:", e)

    @staticmethod
    def get_fname(fname):
        """ Returns the name only of a file without path or file extension """
        head, tail = ntpath.split(fname)
        nopath_name = tail or ntpath.basename(head)
        return nopath_name.strip(".inkml")


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
            with open(grammar_file) as f:
                for line in f:
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
                tracelisttemp[traceid] = Trace(traceid, trace.text)

            #get all symbols
            symbollist = []
            toptracegroup = root.find('inkml:traceGroup', ns)
            for subTraceGroup in toptracegroup.findall('inkml:traceGroup', ns):  # for each symbol
                annotationXML = subTraceGroup.find('inkml:annotationXML',ns).attrib['href']
                annotation = subTraceGroup.find('inkml:annotation', ns).text
                if annotation is None:
                    annotation = "No_Label"
                #get tracelist for symbol
                traceviewlisttemp = []
                for traceview in subTraceGroup.findall('inkml:traceView', ns):
                    id = int(traceview.attrib['traceDataRef'])
                    traceviewlisttemp.append(id)
                tracelist = [tracelisttemp[k] for k in traceviewlisttemp]  # trace subset for symbol
                # find what index this symbol corresponds to
                assert annotation in self.grammar, "Error: " + annotation + " is not defined in the grammar"
                label_index = self.grammar[annotation]
                symbollist.append(Symbol(annotation, annotationXML, label_index, tracelist))

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


def print_usage():
    """ Prints correct usage of the program and exits """

    print("$ python3 parseInkml [flag] [arguments]")
    print("flags:")
    print("  -t <params.txt>     : train classifier with optional output file (no flag set will perform testing)")
    print("  -p [params.txt]     : load parameters for testing from params.txt instead of default location")
    print("  -d [dir1 dir2...]   : operate on the specified directories")
    print("  -f [file1 file2...] : operate on the specified files")
    print("  -l [filelist.txt]   : operate on the files listed in the specified text file")
    print("  -o [outdir]         : specify the output directory for .lg files")
    print("  -v [int]            : turn on verbose output [1=minimal, 2=maximal]")
    print("  -g [file]           : specify grammar file location")
    sys.exit(1)

@profile
def main():
    """
    This is the pipeline of the system
    """
    # :TODO specify the output directory

    if len(sys.argv) < 3:
        print_usage()

    testing = True
    verbose = 0
    default_param_out = "params.txt"
    default_lg_out = ".\\output\\"
    grammar_file = "listSymbolsPart4-revised.txt"

    print("Running", sys.argv[0])
    if "-v" in sys.argv:
        index = sys.argv.index("-v")
        if index < len(sys.argv) - 1 and "-" not in sys.argv[index+1]:
            verbose = int(sys.argv[index+1])
            sys.argv.remove(sys.argv[index+1])
        print("-v : using verbose output level", verbose)
        sys.argv.remove("-v")
    if "-g" in sys.argv:  # setting grammar file location
        index = sys.argv.index("-g")
        if index < len(sys.argv) - 1 and "-" not in sys.argv[index+1]:
            grammar_file = sys.argv[index+1]
            sys.argv.remove(grammar_file)
        sys.argv.remove("-g")
        print("-g: grammar file loaded from", grammar_file)
    else:
        print("-g not set: grammar file loaded from", grammar_file)
    if "-t" in sys.argv:
        index = sys.argv.index("-t")
        if index < len(sys.argv) - 1 and "-" not in sys.argv[index+1]:
            default_param_out = sys.argv[index+1]
            sys.argv.remove(default_param_out)
        sys.argv.remove("-t")
        testing = False
        print("-t : training the classifier and saving parameters to", default_param_out)
    else:
        if "-p" in sys.argv:
            index = sys.argv.index("-p")
            if index < len(sys.argv) - 1 and "-" not in sys.argv[index+1]:
                default_param_out = sys.argv[index + 1]
                sys.argv.remove(default_param_out)
            sys.argv.remove("-p")
            print("-p set,", end=" ")
        print("-t not set : testing the classifier from parameters saved in", default_param_out)

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
    if verbose == 2:
        p.print_results()

    # STEP 2 - SPLITTING (ONLY FOR TRAINING) AND
    # STEP 3 - FEATURE EXTRACTION
    if not testing:
        print("\n########### Splitting input data ###########")
        s = Split(p.parsed_inkml, p.grammar, verbose)
        s.optimize_cosine()
        print("\n######## Running feature extraction ########")
        f = FeatureExtraction(verbose)
        if verbose == 2:
            for inkmlFile in s.train:
                for symbol in inkmlFile.symbol_list:
                    symbol.print_traces()
        for inkmlFile in s.train:
            for symbol in inkmlFile.symbol_list:
                for trace in symbol.trace_list:
                    trace_mat = f.convert_to_image(trace.x, trace.y)
                    print(inkmlFile.fname, symbol.label, trace.id)
                    print(trace_mat)
                    fig = plt.figure()
                    ax = fig.add_subplot(1,1,1)
                    ax.set_aspect('equal')
                    plt.imshow(trace_mat)
                    plt.show()
        xgrid_train, ytclass_train, inkmat_train = f.get_feature_set(s.train, verbose)
        xgrid_test, ytclass_test, inkmat_test = f.get_feature_set(s.test, verbose)

    else:
        print("\n######## Running feature extraction ########")
        f = FeatureExtraction(verbose)
        xgrid_test, ytclass_test, inkmat_test = f.get_feature_set(p.parsed_inkml, verbose)

    # STEP 4 - CLASSIFICATION and WRITING LG FILES
    if not testing:
        print("\n########## Training the classifier #########")
        c = Classifier(train_data=xgrid_train, train_targ=ytclass_train, grammar=p.grammar, verbose=verbose)
        c.test_classifiers(xgrid_train, test_targ=ytclass_train, inkml=inkmat_train, outdir=default_lg_out + "train\\")
    else:
        c = Classifier(param_file=default_param_out)
    print("\n########## Running classification ##########")
    c.test_classifiers(xgrid_test, test_targ=ytclass_test, inkml=inkmat_test, outdir=default_lg_out + "test\\")


if __name__ == '__main__':
    main()