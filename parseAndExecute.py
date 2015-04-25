import xml.etree.ElementTree as ET
import os
import sys
import subprocess
from split import *
from features import *
from classifier import *
from profilehooks17.profilehooks import *


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
        if labelXML != None:
            if labelXML[0:2] != ",_":
                self.labelXML = labelXML
            else:
                self.labelXML = "COMMA" + labelXML[1:]
        else:
            self.labelXML = labelXML
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

    def __init__(self, label, fname, symbol_list):
        self.label = label
        self.fname = self.get_fname(fname)
        self.symbol_list = symbol_list
        self.class_decisions = [0]*len(symbol_list)
        # call the crohmeToLg tool in order to get the relationship info
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
        #sort to obtain inkml ordering
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
                    self.grammar[sym] = i
                    if sym != ",":
                        self.grammar_inv[i] = sym
                    else:
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
            if self.verbose == 1:
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


def print_usage():
    """ Prints correct usage of the program and exits """
    print("$ python3 parseAndExecute.py [flag] [arguments]")
    print("flags:")
    print("  -t <model_dir>      : train classifier (no flag set will perform testing)")
    print("  -m [name]           : specify model to use for testing (inside params dir)")
    print("      Options: '1nn.pkl' - 1-nearest neighbor")
    print("               'rf.pkl' - random forest")
    print("               'bdt.pkl' - AdaBoost with decision tree weak learners")
    print("               'rbf_svm.pkl' - SVM with RBF kernel")
    print("  -p [params]         : load parameters for testing from params dir instead of default location")
    print("  -d [dir1 dir2...]   : operate on the specified directories")
    print("  -f [file1 file2...] : operate on the specified files")
    print("  -l [filelist.txt]   : operate on the files listed in the specified text file")
    print("  -o [outdir]         : specify the output directory for .lg files")
    print("  -v [int]            : turn on verbose output [1=minimal, 2=maximal]")
    print("  -g [file]           : specify grammar file location")
    print("  -skip               : flag to skip the parsing step and load from parsed.pkl")
    sys.exit(1)


def pickle_array(mat, name):
    with open(os.path.relpath(name), 'wb') as handle:
        pickle.dump(mat, handle, pickle.HIGHEST_PROTOCOL)


def unpickle(name):
    with open(os.path.relpath(name), 'rb') as handle:
        tmp = pickle.load(handle)
    return tmp


@profile
def main():
    """
    This is the pipeline of the system
    """

    if len(sys.argv) < 3:
        print_usage()

    testing = True
    verbose = 0
    default_param_out = os.path.realpath("models")
    default_lg_out = os.path.realpath("output")
    grammar_file = "listSymbolsPart4-revised.txt"
    model = "rf.pkl"
    skip = False

    print("Running", sys.argv[0])
    if "-v" in sys.argv:
        index = sys.argv.index("-v")
        if index < len(sys.argv) - 1 and "-" not in sys.argv[index+1]:
            verbose = int(sys.argv[index+1])
            sys.argv.remove(sys.argv[index+1])
        print("-v : using verbose output level", verbose)
        sys.argv.remove("-v")
    if "-o" in sys.argv:
        index = sys.argv.index("-o")
        if index < len(sys.argv) - 1 and "-" not in sys.argv[index+1]:
            default_lg_out = os.path.realpath(sys.argv[index+1])
            sys.argv.remove(sys.argv[index+1])
        print("-o : using output directory", default_lg_out)
        sys.argv.remove("-o")
    else:
        print("-o not set: output will be sent to", default_lg_out)
    if "-g" in sys.argv:  # setting grammar file location
        index = sys.argv.index("-g")
        if index < len(sys.argv) - 1 and "-" not in sys.argv[index+1]:
            grammar_file = sys.argv[index+1]
            sys.argv.remove(grammar_file)
        sys.argv.remove("-g")
        print("-g: grammar file loaded from", grammar_file)
    else:
        print("-g not set: grammar file loaded from", grammar_file)
    if "-skip" in sys.argv:
        sys.argv.remove("-skip")
        skip = True
        print("Skipping parse step and loading from parsed.pkl")
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
        print("-t not set : testing the classifier from parameters saved in directory", default_param_out)
    if "-m" in sys.argv:
        index = sys.argv.index("-m")
        if index < len(sys.argv) - 1 and "-" not in sys.argv[index+1]:
            model = sys.argv[index+1]
            sys.argv.remove(model)
            print("-m : using model", model)
        sys.argv.remove("-m")
    elif testing:
        print("-m not set: testing with", model)

    # STEP 1 - PARSING (if not saved)
    if not skip:
        print("\n############ Parsing input data ############")
        p = Parser(verbose, grammar_file)
        if sys.argv[1] == "-f":  # operate on files
            p.parse(sys.argv[2:])
        elif sys.argv[1] == "-d":  # operate on directories
            filelist = []
            for arg in sys.argv[2:]:
                for filename in os.listdir(arg):
                    filelist.append(os.path.join(arg, filename))
            p.parse(filelist)
        elif sys.argv[1] == "-l":  # operate on a filelist
            path = os.path.dirname(os.path.realpath(sys.argv[2]))
            print(path)
            flist = []
            f = open(sys.argv[2])
            for line in f:
                flist.append(os.path.join(path, os.path.normcase(line.strip())))
            p.parse(flist)
            f.close()
        else:
            print("Usage error:")
            print_usage()
        print("Parsed", len(p.parsed_inkml), "InkML files")
        if verbose == 2:
            p.print_results()
        pickle_array(p, "parsed.pkl")
    # LOAD SAVED PARSED FILE
    else:
        print("opening parsed XML from file parsed.pkl")
        p = unpickle("parsed.pkl")

    # TRAINING PATH OF EXECTION
    if not testing:
        # Skip feature extraction to save time
        if skip:
            print("opening features from x_train.pkl, x_test.pkl")
            xgrid_train = unpickle("x_train.pkl")
            ytclass_train = unpickle("y_train.pkl")
            inkmat_train = unpickle("inkmat_train.pkl")
            xgrid_test = unpickle("x_test.pkl")
            ytclass_test = unpickle("y_test.pkl")
            inkmat_test = unpickle("inkmat_test.pkl")
        else:
            # STEP 2 - SPLITTING
            print("\n########### Splitting input data ###########")
            s = Split(p.parsed_inkml, p.grammar, verbose)
            s.optimize_kl()
            # STEP 3 - FEATURE EXTRACTION
            print("\n######## Running feature extraction ########")
            f = FeatureExtraction(verbose)
            if verbose == 2:
                for inkmlFile in s.train:
                    for symbol in inkmlFile.symbol_list:
                        print(inkmlFile.fname, symbol.label)
                        f.convert_and_plot(symbol.trace_list)
            xgrid_train, ytclass_train, inkmat_train = f.get_feature_set(s.train, True, verbose)
            pickle_array(xgrid_train, "x_train.pkl")
            pickle_array(ytclass_train, "y_train.pkl")
            pickle_array(inkmat_train, "inkmat_train.pkl")
            xgrid_test, ytclass_test, inkmat_test = f.get_feature_set(s.test, False, verbose)
            pickle_array(xgrid_test, "x_test.pkl")
            pickle_array(ytclass_test, "y_test.pkl")
            pickle_array(inkmat_test, "inkmat_test.pkl")

        # STEP 4 - CLASSIFICATION AND WRITING LG FILES FOR TRAINING SET
        print("\n########## Training the classifier #########")
        c = Classifier(param_dir=default_param_out, train_data=xgrid_train, train_targ=ytclass_train,
                       inkml=inkmat_train, grammar=p.grammar_inv, verbose=verbose, outdir=default_lg_out)
                       
                       
        #f = FeatureExtraction(verbose)
        for inkmlfile in s.test:
            trace_list = inkmlfile.get_trace_list()
            best = []
            backtrack = []
            bestclass = []
            
            #input to eval is a list of traces - need to get feature set for this
            
            temp_symbol = Symbol(None,None,None,None,[trace_list[0]])
            feature_set = f.get_single_feature_set(temp_symbol,0)
            maxkey, maxdist = c.eval(feature_set,1,0)
            print("maxkey", maxkey)
            print("maxdist", maxdist)
            best.append(maxdist) #index 0
            backtrack.append(-1) #indicates start of array
            bestclass.append(maxkey)
            for i in range(1, len(trace_list)):
                print("-----")
                best.append(float("-inf"))
                backtrack.append(-1)
                bestclass.append("temp")
                for j in range(i-1, -1,-1):
                    #print(i, ", ", j, ", ", best[j])
                    subset = trace_list[j+1:i+1]
                    print("subset: ", j+1, ", ", i+1)
                    temp_symbol = Symbol(None,None,None,None,subset)
                    feature_set = f.get_single_feature_set(temp_symbol,0)
                    maxkey, maxdist = c.eval(feature_set,len(subset),0)
                    
                    print("maxkey: ", maxkey, "maxdist: ", maxdist)
                    dist = best[j] + maxdist
                    #print(dist)
                    #print(best[i])
                    if dist > best[i]:
                        #print("got here")
                        best[i] = dist
                        backtrack[i] = j
                        bestclass[i] = maxkey
                #special case: all traces up to and including i are one character
                temp_symbol = Symbol(None,None,None,None,trace_list[0:i+1])
                feature_set = f.get_single_feature_set(temp_symbol,0)
                maxkey, maxdist = c.eval(feature_set,(i+1),0)
                if maxdist > best[i]:
                    best[i] = maxdist
                    backtrack[i] = -1
                    bestclass[i] = maxkey
            print(best)
            print(backtrack)
            print(bestclass)
            print("")
            print("")
            print("")
    # TESTING PATH OF EXECUTION
    else:
        print("\n######## Running feature extraction ########")
        f = FeatureExtraction(verbose)
        xgrid_test, ytclass_test, inkmat_test = f.get_feature_set(p.parsed_inkml, True, verbose)
        c = Classifier(param_dir=default_param_out, testing=testing, grammar=p.grammar_inv, verbose=verbose, outdir=default_lg_out, model=model)
            
    # STEP 4 - CLASSIFICATION AND WRITING LG FILES FOR TESTING SET
    
    #have to parse segmentation output into inkml file set, then run classifiers
    '''print("\n########## Running classification ##########")
    c.test_classifiers(xgrid_test, test_targ=ytclass_test, inkml=inkmat_test)'''


if __name__ == '__main__':
    main()