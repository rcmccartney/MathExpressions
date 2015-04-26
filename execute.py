import sys
from code.commandLineOpts import parse_cl
from code.split import *
from code.features import *
from code.classifier import *
from code.parse import *
from code.segmentation import *
#from profilehooks17.profilehooks import *


def pickle_array(mat, name):
    with open(os.path.relpath(name), 'wb') as handle:
        pickle.dump(mat, handle, pickle.HIGHEST_PROTOCOL)


def unpickle(name):
    with open(os.path.relpath(name), 'rb') as handle:
        tmp = pickle.load(handle)
    return tmp


#@profile
def main():
    """
    This is the pipeline of the system
    """
    parsing, splitting, extraction, testing, train_percent, \
        segment, model, filelist, default_model_out, \
        default_lg_out, verbose, grammar_file = parse_cl(sys.argv)

    # STEP 1 - PARSING
    if parsing:
        print("\n############ Parsing input data ############")
        p = Parser(verbose, grammar_file)
        p.parse(filelist)
        print("Parsed", len(p.parsed_inkml), "InkML files")
        if verbose == 2:
            p.print_results()
        if not testing:
            pickle_array(p, "parsed_train.pkl")
        else:
            pickle_array(p, "parsed_test.pkl")

    # STEP 2 - SPLITTING
    if splitting:
        p = unpickle("parsed_train.pkl")
        print("\n########### Splitting input data for training ###########")
        s = Split(p.parsed_inkml, p.grammar, verbose, train_percent)
        if train_percent < 1:
            s.optimize_kl()
        if verbose == 2:
            for inkmlFile in s.train:
                for symbol in inkmlFile.symbol_list:
                    print(inkmlFile.fname, symbol.label)
        pickle_array(s, "split.pkl")

    # STEP 3 - EXTRACTION
    if extraction and not testing:
        s = unpickle("split.pkl")
        print("\n######## Running feature extraction for training ########")
        f = FeatureExtraction(verbose)
        xgrid_train, ytclass_train, inkmat_train = f.get_feature_set(s.train, True, verbose)
        pickle_array(xgrid_train, "x_train.pkl")
        pickle_array(ytclass_train, "y_train.pkl")
        pickle_array(inkmat_train, "inkmat_train.pkl")
        if s.split_percent < 1:
            xgrid_test, ytclass_test, inkmat_test = f.get_feature_set(s.test, False, verbose)
            pickle_array(xgrid_test, "x_test.pkl")
            pickle_array(ytclass_test, "y_test.pkl")
            pickle_array(inkmat_test, "inkmat_test.pkl")
    elif extraction and not segment:  # For testing the classifier only
        p = unpickle("parsed_test.pkl")
        print("\n######## Running feature extraction for testing ########")
        f = FeatureExtraction(verbose)
        xgrid_test, ytclass_test, inkmat_test = f.get_feature_set(p.parsed_inkml, False, verbose)
        pickle_array(xgrid_test, "x_test.pkl")
        pickle_array(ytclass_test, "y_test.pkl")
        pickle_array(inkmat_test, "inkmat_test.pkl")

    # STEP 3 - TRAINING CLASSIFIER
    if not testing:
        p = unpickle("parsed_train.pkl")
        s = unpickle("split.pkl")
        xgrid_train = unpickle("x_train.pkl")
        ytclass_train = unpickle("y_train.pkl")
        inkmat_train = unpickle("inkmat_train.pkl")
        print("\n########## Training the classifier #########")
        c = Classifier(param_dir=default_model_out, train_data=xgrid_train, train_targ=ytclass_train,
                       inkml=inkmat_train, grammar=p.grammar_inv, verbose=verbose, outdir=default_lg_out)
        # Can test the classifer on the held out data
        if not segment and s.split_percent < 1:
            xgrid_test = unpickle("x_test.pkl")
            ytclass_test = unpickle("y_test.pkl")
            inkmat_test = unpickle("inkmat_test.pkl")
            c.test_classifiers(xgrid_test, test_targ=ytclass_test, inkml=inkmat_test)
    else:
        p = unpickle("parsed_test.pkl")
        c = Classifier(param_dir=default_model_out, testing=testing, grammar=p.grammar_inv,
                       verbose=verbose, outdir=default_lg_out, model=model)
        if not segment:  # JUST FOR TESTING THE CLASSIFIER
            xgrid_test = unpickle("x_test.pkl")
            ytclass_test = unpickle("y_test.pkl")
            inkmat_test = unpickle("inkmat_test.pkl")
            c.test_classifiers(xgrid_test, test_targ=ytclass_test, inkml=inkmat_test)
        # LAST STEP - PERFORMING SEGMENTATION
        # Using dynamic programming for segmentation,
        # input inkml list, feature extractor, and classifier objects
        else:  # testing = True, segment = True
            p = unpickle("parsed_test.pkl")
            f = FeatureExtraction(verbose)
            seg = Segmenter()
            seg.segment_inkml_files(p.parsed_inkml, f, c)


if __name__ == '__main__':
    main()