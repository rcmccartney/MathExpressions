import sys
import random
import pickle
from code.commandLineOpts import parse_cl
from code.split import *
from code.features import *
from code.classifier import *
from code.parse import *
from code.segmentation import *

from code.equationparser import *
#from profilehooks17.profilehooks import *


def pickle_array(mat, adir, name):
    if not os.path.exists(adir):
        os.makedirs(adir)
    with open(os.path.join(adir, os.path.relpath(name)), 'wb') as handle:
        pickle.dump(mat, handle, pickle.DEFAULT_PROTOCOL)


def unpickle(adir, name):
    with open(os.path.join(adir, os.path.relpath(name)), 'rb') as handle:
        tmp = pickle.load(handle)
    return tmp


def isFile(adir, name):
    return os.path.isfile(os.path.join(adir, os.path.relpath(name)))


#@profile
def main():
    """
    This is the pipeline of the system
    """
    conversion, parsing, splitting, extraction, training, testing, \
        train_percent, segment, model, filelist, default_model_out,\
        default_lg_out, grammar_file = parse_cl(sys.argv)

    # get the output classes we will use
    g = Grammar(grammar_file)

    # STEP 1 - CONVERTING INKML FILES
    if conversion:
        print("\n# Converting input inkml files #")
        p = Parser()
        p.parse(filelist, g.grammar)
        print("Parsed", len(p.parsed_inkml), "InkML files")
        if not testing:
            pickle_array(p, default_lg_out, "parsed_train.pkl")
        else:
            pickle_array(p, default_lg_out, "parsed_test.pkl")

    # STEP 2 - SPLITTING
    if splitting:
        print("\n# Splitting input data for training #")
        assert isFile(default_lg_out, "parsed_train.pkl"), "You must have parsed training data before you can split"
        p = unpickle(default_lg_out, "parsed_train.pkl")
        s = Split(p.parsed_inkml, g.grammar, train_percent)
        if train_percent < 1:
            s.optimize_kl()
        pickle_array(s, default_lg_out, "split.pkl")

    # STEP 3 - EXTRACTION
    if extraction and not testing:
        print("\n# Running feature extraction for training data #")
        assert isFile(default_lg_out, "split.pkl"), "You must have split the input data before feature extraction"
        s = unpickle(default_lg_out, "split.pkl")
        f = FeatureExtraction()
        pickle_array(f.get_feature_set(s.train, True), default_lg_out, "train_feat.pkl")
        if s.split_percent < 1:
            pickle_array(f.get_feature_set(s.test, False), default_lg_out, "test_feat.pkl")
        pickle_array(f, default_lg_out, "features.pkl")
    elif extraction and not segment:  # For testing the classifier w/o segmentation - segmentation given to you
        print("\n# Running feature extraction for testing the classifier #")
        assert isFile(default_lg_out, "parsed_test.pkl"), \
            "You must have parsed test data before testing the classifier"
        assert isFile(default_lg_out, "features.pkl"), "You must have a trained feature extractor before testing"
        p = unpickle(default_lg_out, "parsed_test.pkl")
        f = unpickle(default_lg_out, "features.pkl")
        pickle_array(f.get_feature_set(p.parsed_inkml, False), default_lg_out, "test_feat.pkl")

    # STEP 3 - TRAINING CLASSIFIER
    if training:
        print("\n# Training the classifier #")
        assert isFile(default_lg_out, "split.pkl"), \
            "You must have split the training data before training the classifier"
        assert isFile(default_lg_out, "train_feat.pkl"), \
            "You must have performed feature extraction before training the classifier"
        s = unpickle(default_lg_out, "split.pkl")
        xgrid_train, ytclass_train, inkmat_train = unpickle(default_lg_out, "train_feat.pkl")
        c = Classifier(param_dir=default_model_out, train_data=xgrid_train, train_targ=ytclass_train, model=model,
                       inkml=inkmat_train, grammar=g.grammar_inv, outdir=os.path.join(default_lg_out, "classifier"))
        # Can test the classifer on the held out data
        if not segment and s.split_percent < 1:
            assert isFile(default_lg_out, "test_feat.pkl"), \
                "You must have performed feature extraction on held out data before testing the classifier"
            xgrid_test, ytclass_test, inkmat_test = unpickle(default_lg_out, "test_feat.pkl")
            c.test_classifiers(xgrid_test, test_targ=ytclass_test, inkml=inkmat_test)

    # This is just for testing the classifier, no segmentation required
    if testing and not segment and not parsing:
        print("\n# Testing the classifier only #")
        assert isFile(default_lg_out, "test_feat.pkl"), \
            "You must have performed feature extraction on held out data before testing the classifier"
        xgrid_test, ytclass_test, inkmat_test = unpickle(default_lg_out, "test_feat.pkl")
        c = Classifier(param_dir=default_model_out, testing=True, grammar=g.grammar_inv,
                       outdir=os.path.join(default_lg_out, "classifier"), model=model)
        c.test_classifiers(xgrid_test, test_targ=ytclass_test, inkml=inkmat_test)

    # STEP 4 - SEGMENTATION
    if segment:
        assert isFile(default_lg_out, "features.pkl"), "You must have a trained feature extractor before segmentation"
        f = unpickle(default_lg_out, "features.pkl")
        # two cases - if this is training, use the split test data
        # otherwise, use parsed test data
        inkml_to_parse = None
        if not testing:
            print("\n# Segmenting on training data #")
            assert isFile(default_lg_out, "split.pkl"), \
                "You must have a splitter for training and testing of segmentation"
            s = unpickle(default_lg_out, "split.pkl")
            inkml_to_parse = s.train
            c = Classifier(param_dir=default_model_out, testing=True, grammar=g.grammar_inv,
                           outdir=default_lg_out, model=model)
            seg = Segmenter(grammar=g.grammar_inv)
            # USING A RANDOM SAMPLE TO TRAIN / TEST SEGMENTER
            seg.segment_inkml_files(s.train, f, c)
            seg.backtrack_and_print(os.path.join(default_lg_out, "train", "segment", model.replace(".pkl", "")))
            if s.split_percent < 1:
                seg.segment_inkml_files(s.test, f, c)
                seg.backtrack_and_print(os.path.join(default_lg_out, "test", "segment", model.replace(".pkl", "")))
                inkml_to_parse = s.test
        else:
            print("\n# Segmenting on unseen test data #")
            assert isFile(default_lg_out, "parsed_test.pkl"), "You must have parsed testing data to segment"
            p = unpickle(default_lg_out, "parsed_test.pkl")
            c = Classifier(param_dir=default_model_out, testing=True, grammar=g.grammar_inv,
                           outdir=default_lg_out, model=model)
            seg = Segmenter(grammar=g.grammar_inv)
            seg.segment_inkml_files(p.parsed_inkml, f, c)
            seg.backtrack_and_print(os.path.join(default_lg_out, "test", "segment", model.replace(".pkl", "")))
            inkml_to_parse = p.parsed_inkml

    # STEP 5 - PARSING
    if parsing and segment:
        print("\n# Parsing Equations from previous classification and segmentation steps #")
        par = Equationparser()
        # segmented symbols are the symbols that have been segmented and classified, not ground truth
        for inkmlfile in inkml_to_parse:
            print("Parsing " + inkmlfile.fname)
            res = par.parse_equation(inkmlfile.segmented_symbols)
            inkmlfile.print_gt(os.path.join(default_lg_out, "parse_all"), res, use_segmention=True)
    elif parsing:
        #perform the equation parse on known segmentation
        print("\n# Parsing Equations from ground truth classification and segmentation #")
        if testing:
            assert isFile(default_lg_out, "parsed_test.pkl"), "You must have converted test data to parse"
            data = unpickle(default_lg_out, "parsed_test.pkl").parsed_inkml
        else:
            if not splitting:
                assert isFile(default_lg_out, "parsed_train.pkl"), "You must have converted data to parse"
                data = unpickle(default_lg_out, "parsed_train.pkl").parsed_inkml
            else:  # you already split the data, take the test set
                data = unpickle(default_lg_out, "split.pkl").test
        par = Equationparser()
        for inkmlfile in data:
            print("Parsing " + inkmlfile.fname)
            res = par.parse_equation(inkmlfile.symbol_list)
            inkmlfile.print_gt(os.path.join(default_lg_out, "parse_gt"), res)


if __name__ == '__main__':
    main()