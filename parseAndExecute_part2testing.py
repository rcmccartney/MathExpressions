import xml.etree.ElementTree as ET
import os
import sys
import ntpath
import subprocess
from split import *
from features import *
from classifier import *
#from profilehooks17.profilehooks import *


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


#@profile
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
    model = "rf"
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
        with open(os.path.relpath("parsed.pkl"), 'wb') as handle:
            pickle.dump(p, handle, pickle.HIGHEST_PROTOCOL)
    # LOAD SAVED PARSED FILE
    else:
        with open(os.path.relpath("parsed.pkl"), 'rb') as handle:
            p = pickle.load(handle)

    # TRAINING PATH OF EXECTION
    if not testing:
        # STEP 2 - SPLITTING
        print("\n########### Splitting input data ###########")
        s = Split(p.parsed_inkml, p.grammar, verbose)
        s.optimize_kl()
        # STEP 3 - FEATURE EXTRACTION
        print("\n######## Running feature extraction ########")
        f = FeatureExtraction(verbose)
        '''if verbose == 2:
            for inkmlFile in s.train:
                for symbol in inkmlFile.symbol_list:
                    print(inkmlFile.fname, symbol.label)
                    f.convert_and_plot(symbol.trace_list)

        xgrid_train, ytclass_train, inkmat_train = f.get_feature_set(s.train, verbose)
        xgrid_test, ytclass_test, inkmat_test = f.get_feature_set(s.test, verbose)
        # STEP 4 - CLASSIFICATION AND WRITING LG FILES FOR TRAINING SET
        print("\n########## Training the classifier #########")
        c = Classifier(param_dir=default_param_out, train_data=xgrid_train, train_targ=ytclass_train,
                       inkml=inkmat_train, grammar=p.grammar_inv, verbose=verbose, outdir=default_lg_out)'''
    # TESTING PATH OF EXECUTION
    '''else:
        print("\n######## Running feature extraction ########")
        f = FeatureExtraction(verbose)
        xgrid_test, ytclass_test, inkmat_test = f.get_feature_set(p.parsed_inkml, verbose)
        c = Classifier(param_dir=default_param_out, testing=testing, grammar=p.grammar_inv, verbose=verbose,
                       outdir=default_lg_out, model=model)'''

    # STEP 4 - CLASSIFICATION AND WRITING LG FILES FOR TESTING SET
    '''print("\n########## Running classification ##########")
    c.test_classifiers(xgrid_test, test_targ=ytclass_test, inkml=inkmat_test)'''


    def train(training_set):
        #train custom set
        train_data = {}
        train_data_freq = {}
        for inkmlfile in training_set:
            for symbol in inkmlfile.symbol_list:
                templabel = symbol.label
                tempimage = np.ravel(f.convert_to_image(symbol.trace_list))
                if templabel not in train_data:
                    train_data[templabel] = np.add(np.zeros(21*21),tempimage)
                    train_data_freq[templabel] = 1
                else:
                    train_data[templabel] = np.add(train_data[templabel],tempimage)
                    train_data_freq[templabel] += 1
        for key in train_data:
            count = train_data_freq[key]
            train_data[key] /= count
        print(train_data)
        return train_data
        
    def eval(input, train_data): #input is list of Trace objects, single image
        test_image = f.convert_to_image(input)
        minDist = float("inf")
        minKey = ""
        for key in train_data:
            dist = np.linalg.norm(np.ravel(test_image) - np.ravel(train_data[key]))
            dist /= np.sum(test_image)
            dist *= float(len(input))
            if dist < minDist:
                minDist = dist
                minKey = key
        return minKey, minDist
        
    train_data = train(s.train)
    for inkmlfile in s.test:
        trace_list = inkmlfile.get_trace_list()
        best = []
        backtrack = []
        bestclass = []
        
        minkey, mindist = eval([trace_list[0]],train_data)
        best.append(mindist) #index 0
        backtrack.append(-1) #indicates start of array
        bestclass.append(minkey)
        for i in range(1, len(trace_list)):
            #print("-----")
            best.append(float("inf"))
            backtrack.append(-1)
            bestclass.append("temp")
            for j in range(i-1, -1,-1):
                #print(i, ", ", j, ", ", best[j])
                subset = trace_list[j+1:i+1]
                minkey, mindist = eval(subset,train_data)
                
                dist = best[j] + mindist
                #print(dist)
                #print(best[i])
                if dist < best[i]:
                    #print("got here")
                    best[i] = dist
                    backtrack[i] = j
                    bestclass[i] = minkey
            #special case: all traces up to and including i are one character
            minkey, mindist = eval(trace_list,train_data)
            if mindist < best[i]:
                best[i] = mindist
                backtrack[i] = -1
                bestclass[i] = minkey
        print(best)
        print(backtrack)
        print(bestclass)
        
            
if __name__ == '__main__':
    main()