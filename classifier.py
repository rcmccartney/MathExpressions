__author__ = 'mccar_000'

import os
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from classifierImplementations import *
from sklearn import svm


class Classifier():
    """ This class is a wrapper around whatever classifiers are implemented for the inkml classification """

    def __init__(self, outdir=None, train_data=None, train_targ=None, grammar=None, verbose=None,
                 inkml=None, param_file=None):
        """
        :param param_file: the parameters to use if testing, or the location to save for training
        :param verbose: boolean to print verbose output for debugging
        """
        self.verbose = verbose
        if param_file is not None:
            self.load_saved_classifiers()
        else:
            self.train_data = train_data
            self.train_target = train_targ
            self.grammar = grammar
            self.classifiers = []
            self.outdir = outdir
            self.train_classifiers(inkml, verbose)

    def train_classifiers(self, inkml, verbose):
        """ Trains the classifiers being used.  Modify this to introduce other classifiers """

        print("** Training 1-nn **")
        knn = KnnClassifier(k=1)
        knn.fit(self.train_data, self.train_target)
        out = knn.predict(self.train_data)
        self.make_lg(out, inkml, os.path.join(self.outdir, "train", "1nn"))
        if verbose == 1:
            self.print_confusion(self.train_target, out)

        print("** Training AdaBoost **")
        # Create and fit an AdaBoosted decision tree
        bdt = AdaBoostClassifier(DecisionTreeClassifier(max_depth=8),
                                 algorithm="SAMME", n_estimators=200)
        bdt.fit(self.train_data, self.train_target)
        out = bdt.predict(self.train_data)
        self.make_lg(out, inkml, os.path.join(self.outdir, "train", "bdt"))
        if verbose == 1:
            self.print_confusion(self.train_target, out)

        print("** Training Random Forest **")
        rf = RandomForestClassifier(n_estimators=200)
        rf.fit(self.train_data, self.train_target)
        out = rf.predict(self.train_data)
        self.make_lg(out, inkml, os.path.join(self.outdir, "train", "rf"))
        if verbose == 1:
            self.print_confusion(self.train_target, out)

        #print("** Training Neural Network **")
        #ff = FFNeural(len(self.grammar))
        #ff.fit(self.train_data, self.train_target, 100)
        #if verbose == 1:
        #    self.print_confusion(self.train_target, ff.predict(self.train_data))
        #print("** Training LSTM **")
        #lstm = LSTMNeural(len(self.grammar))
        #lstm.fit(self.train_data, self.train_target, 100)

        print("** Training SVM **")
        rbf_svc = svm.SVC(kernel='rbf')
        rbf_svc.fit(self.train_data, self.train_target)
        out = rbf_svc.predict(self.train_data)
        self.make_lg(out, inkml, os.path.join(self.outdir, "train", "rbf_svm"))
        if verbose == 1:
            self.print_confusion(self.train_target, out)

        self.classifiers = [
                            ("1-NN", "1nn", knn),
                            ("Boosted decision trees", "bdt", bdt),
                            ("Random forest", "rf", rf),
                            ("SVM w/ RBF kernel", "rbf_svm", rbf_svc),
                            #("FF Neural Net", ff),
                            #("LSTM net", lstm),
                            ]

    def make_lg(self, output, inkml, dirname):
        # fill in the inkmls with this output decision
        for i in range(len(output)):
            inkml_file, symbol = inkml[i]  # inkml is tuple of (inkml_file, symbol)
            inkml_file.class_decisions[symbol.num_in_inkml] = output[i]
        # now write each inkml out
        for inkml_file in inkml:
            inkml_file[0].print_it(dirname, self.grammar)

    def test_classifiers(self, test_data, test_targ=None, inkml=None):
        """
        Tests the classifiers trained above on the testing target data.
        If target output is provided then a confusion matrix is created
        """
        for classifier in self.classifiers:
            print("Testing", classifier[0])
            out = classifier[2].predict(test_data)
            self.make_lg(out, inkml, os.path.join(self.outdir, "test", classifier[1]))
            if test_targ is not None:
                self.print_confusion(test_targ, out)

    def print_confusion(self, target, out):
        """
        Makes and prints confusion matrix in nice formatting
        """
        conf = []
        for i in range(len(self.grammar)):
            conf.append([0]*len(self.grammar))
        for i in range(len(target)):
            conf[target[i]][out[i]] += 1
        conf_mat = np.asarray(conf)
        print("Classification rate: {:.2f}%".format(100*(np.trace(conf_mat) / np.sum(conf_mat))))
        if self.verbose == 2:
            print("Targ/Out", end=" ")
            for i in range(conf_mat.shape[0]):
                print("{:4d}".format(i), end=" ")
            for i in range(conf_mat.shape[0]):
                print("\n", "{:4d}".format(i), end="    ")
                for j in range(conf_mat.shape[1]):
                    print("{:4d}".format(conf_mat[i, j]), end=" ")
            print()

    def load_saved_classifiers(self):
        # :TODO load saved classifier parameters
        """ this loads the saved parameters from the last training of the system """
        self.classifiers = []