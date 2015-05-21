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
    parsing, splitting, extraction, training, testing, \
        train_percent, segment, model, filelist, default_model_out,\
        default_lg_out, grammar_file = parse_cl(sys.argv)

    # get the output classes we will use
    g = Grammar(grammar_file)

    # STEP 1 - PARSING
    if parsing:
        print("\n# Parsing input data #")
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

    ###########TEMP TEMP TEMP####################
    #perform the equation parse on known segmentation
    print("\n# Parsing Equation #")
    assert isFile(default_lg_out, "split.pkl"), "You must have split"
    par = Equationparser()
    for inkmlfile in s.train:
        res = par.parse_equation(inkmlfile.symbol_list)
        print(inkmlfile.fname)
        for r in res:
            print(r)
        print("\n\n")
    
        
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
    if testing and not segment:
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
        if not testing:
            print("\n# Segmenting on training data #")
            assert isFile(default_lg_out, "split.pkl"), \
                "You must have a splitter for training and testing of segmentation"
            s = unpickle(default_lg_out, "split.pkl")
            c = Classifier(param_dir=default_model_out, testing=True, grammar=g.grammar_inv,
                           outdir=default_lg_out, model=model)
            seg = Segmenter(grammar=g.grammar_inv)
            # USING A RANDOM SAMPLE TO TRAIN / TEST SEGMENTER
            seg.segment_inkml_files(random.sample(s.train, 200), f, c)
            seg.backtrack_and_print(os.path.join(default_lg_out, "train", "segment", model.replace(".pkl", "")))
            if s.split_percent < 1:
                seg.segment_inkml_files(random.sample(s.test, 200), f, c)
                seg.backtrack_and_print(os.path.join(default_lg_out, "test", "segment", model.replace(".pkl", "")))
        else:
            print("\n# Segmenting on unseen test data #")
            assert isFile(default_lg_out, "parsed_test.pkl"), "You must have parsed testing data to segment"
            p = unpickle(default_lg_out, "parsed_test.pkl")
            c = Classifier(param_dir=default_model_out, testing=True, grammar=g.grammar_inv,
                           outdir=default_lg_out, model=model)
            seg = Segmenter(grammar=g.grammar_inv)
            seg.segment_inkml_files(p.parsed_inkml, f, c)
            seg.backtrack_and_print(os.path.join(default_lg_out, "test", "segment", model.replace(".pkl", "")))


if __name__ == '__main__':
    main()