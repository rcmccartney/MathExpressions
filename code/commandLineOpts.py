import os
import sys


def print_usage():
    """ Prints correct usage of the program and exits """
    print("$ python3 execute.py [flag] [arguments]")
    print("flags:")
    print("  -p                  : perform parsing and save to file")
    print("  -s <percent>        : perform splitting on <percent>% of data in (% in range [0,1]) and save to file")
    print("  -e                  : perform feature extraction and save to file")
    print("  -tc                 : train the classifier with the data passed in, set segment to 1.0 to use all data")
    print("  -test               : perform a complete test with unseen data")
    print("      Options: -seg flag set will test segmentation, otherwise will test only classification")
    print("  -seg                : perform segmentation (will use either training or testing data)")
    print("  -m  [name]          : specify model to use (inside models dir)")
    print("      Options: '1nn.pkl' - 1-nearest neighbor")
    print("               'rf.pkl' - random forest (default)")
    print("               'bdt.pkl' - AdaBoost with decision tree weak learners")
    print("               'rbf_svm.pkl' - SVM with RBF kernel")
    print("  -d [dir1 dir2...]   : operate on the specified directories")
    print("  -f [file1 file2...] : operate on the specified files")
    print("  -l [filelist.txt]   : operate on the files listed in the specified text file")
    print("  -ol [outdir]        : specify the output directory for .lg files")
    print("  -om [dir]           : specify the models directory")
    print("  -g [file]           : specify grammar file location")
    sys.exit(1)


def parse_cl(args):
    """
    This is the pipeline of the system
    """

    if len(args) < 2:
        print_usage()

    # set the defaults
    parsing = False
    extraction = False
    training = False
    testing = False
    train_percent = 0.7
    segment = False
    splitting = False
    model = "rf.pkl"
    filelist = []
    default_model_out = os.path.realpath("models")
    default_lg_out = os.path.realpath("output")
    grammar_file = "listSymbolsPart4-revised.txt"

    print("Running", args[0])
    # ask for help
    if "-h" in args:
        print_usage()
    # parsing setting
    if "-p" in args:
        args.remove("-p")
        parsing = True
        print("-p : parsing input files")
    # extraction setting
    if "-e" in args:
        args.remove("-e")
        extraction = True
        print("-e : performing feature extraction")
    # splitting setting
    if "-s" in args:
        index = args.index("-s")
        if index < len(args)-1 and "-" not in args[index+1]:
            train_percent = float(args[index+1])
            args.remove(args[index+1])
        args.remove("-s")
        splitting = True
        print("-s : splitting the data with", train_percent, "of the data for training")
    # training setting
    if "-tc" in args:
        args.remove("-tc")
        training = True
        print("-tc : training the classifier")
    # segmentation setting
    if "-seg" in args:
        args.remove("-seg")
        segment = True
        print("-seg : performing segmentation")
    # testing setting
    if "-test" in args:
        args.remove("-test")
        testing = True
        if segment:
            print("-test, seg : testing the segmentation")
        else:
            print("-test, !seg : testing the classifier only")
    # model setting
    if "-m" in args:
        index = args.index("-m")
        if index < len(args)-1 and "-" not in args[index+1]:
            model = args[index+1]
            args.remove(model)
        args.remove("-m")
    print("using model", model)
    # output for lg files
    if "-ol" in args:
        index = args.index("-ol")
        if index < len(args)-1 and "-" not in args[index+1]:
            default_lg_out = os.path.realpath(args[index+1])
            args.remove(args[index+1])
        args.remove("-ol")
    print("using lg output directory", default_lg_out)
    # model output dir
    if "-om" in args:
        index = args.index("-om")
        if index < len(args)-1 and "-" not in args[index+1]:
            default_model_out = os.path.realpath(args[index+1])
            args.remove(args[index+1])
        args.remove("-om")
    print("using model directory", default_model_out)
    # setting grammar file location
    if "-g" in args:
        index = args.index("-g")
        if index < len(args)-1 and "-" not in args[index+1]:
            grammar_file = args[index+1]
            args.remove(grammar_file)
        args.remove("-g")
    print("grammar file loaded from", grammar_file)
    # now get the files to use if they are using files
    if len(args) > 1 and args[1] == "-f":  # operate on files
        filelist = args[2:]
    elif len(args) > 1 and args[1] == "-d":  # operate on directories
        for arg in args[2:]:
            for filename in os.listdir(arg):
                filelist.append(os.path.join(arg, filename))
    elif len(args) > 1 and args[1] == "-l":  # operate on a filelist
        path = os.path.dirname(os.path.realpath(args[2]))
        with open(args[2], 'r') as f:
            for line in f:
                filelist.append(os.path.join(path, os.path.normcase(line.strip())))

    return (parsing, splitting, extraction, training, testing,
            train_percent, segment, model, filelist, default_model_out,
            default_lg_out, grammar_file)