import os
import sys


def print_usage():
    """ Prints correct usage of the program and exits """
    print("$ python3 execute.py [flag] [arguments]")
    print("flags:")
    print("  -p  <file>          : perform parsing and save to file")
    print("  -e  <dir>           : perform feature extraction and save to dir")
    print("  -tc <percent>       : train classifier on <percent>% of data")
    print("  -s                  : perform segmentation & testing")
    print("  -m  [name]          : specify model to use (inside models dir)")
    print("      Options: '1nn.pkl' - 1-nearest neighbor")
    print("               'rf.pkl' - random forest")
    print("               'bdt.pkl' - AdaBoost with decision tree weak learners")
    print("               'rbf_svm.pkl' - SVM with RBF kernel")
    print("  -d [dir1 dir2...]   : operate on the specified directories")
    print("  -f [file1 file2...] : operate on the specified files")
    print("  -l [filelist.txt]   : operate on the files listed in the specified text file")
    print("  -ol [outdir]        : specify the output directory for .lg files")
    print("  -om [dir]           : specify the models directory")
    print("  -v [int]            : turn on verbose output [1=minimal, 2=maximal]")
    print("  -g [file]           : specify grammar file location")
    sys.exit(1)


def parse_cl(args):
    """
    This is the pipeline of the system
    """

    if len(args) < 3:
        print_usage()

    # set the defaults
    parsing = False
    extraction = False
    testing = True
    train_percent = 0.7
    segment = False
    model = "rf.pkl"
    filelist = []
    default_model_out = os.path.realpath("models")
    default_lg_out = os.path.realpath("output")
    verbose = 0
    grammar_file = "listSymbolsPart4-revised.txt"

    print("Running", args[0])
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
    # training setting
    if "-tc" in args:
        index = args.index("-tc")
        if index < len(args)-1 and "-" not in args[index+1]:
            train_percent = float(args[index+1])
            args.remove(args[index+1])
        args.remove("-tc")
        testing = False
        print("-tc : training the classifier with", train_percent, "of the data")
    # segmentation setting
    if "-s" in args:
        args.remove("-s")
        segment = True
        print("-s : performing segmentation")
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
    # verbose setting
    if "-v" in args:
        index = args.index("-v")
        if index < len(args) - 1 and "-" not in args[index+1]:
            verbose = int(args[index+1])
            args.remove(args[index+1])
        args.remove("-v")
    print("using verbose output level", verbose)
    # setting grammar file location
    if "-g" in args:
        index = args.index("-g")
        if index < len(args)-1 and "-" not in args[index+1]:
            grammar_file = args[index+1]
            args.remove(grammar_file)
        args.remove("-g")
    print("grammar file loaded from", grammar_file)
    # now get the files to use
    if args[1] == "-f":  # operate on files
        filelist = args[2:]
    elif args[1] == "-d":  # operate on directories
        for arg in args[2:]:
            for filename in os.listdir(arg):
                filelist.append(os.path.join(arg, filename))
    elif args[1] == "-l":  # operate on a filelist
        path = os.path.dirname(os.path.realpath(args[2]))
        print(path)
        f = open(args[2])
        for line in f:
            filelist.append(os.path.join(path, os.path.normcase(line.strip())))
            f.close()
    else:
        print("Usage error:")
        print_usage()

    return (parsing, extraction, testing, train_percent,
            segment, model, filelist, default_model_out,
            default_lg_out, verbose, grammar_file)