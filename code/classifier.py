__author__ = 'mccar_000'

import math
import os
import pickle
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from code.classifierImplementations import *
from sklearn import svm
from sklearn.externals import joblib

class Classifier():
    """ This class is a wrapper around whatever classifiers are implemented for the inkml classification """

    def __init__(self, outdir=None, train_data=None, train_targ=None, grammar=None, verbose=None,
                 inkml=None, param_dir=None, model="rf", testing=False):
        """
        :param param_file: the parameters to use if testing, or the location to save for training
        :param verbose: boolean to print verbose output for debugging
        """
        self.grammar = grammar
        self.inkml = inkml
        self.verbose = verbose
        self.classifiers = []
        self.outdir = outdir
        self.param_dir = param_dir
        if testing:
            self.load_saved_classifier(param_dir, model)
        else:
            self.train_data = train_data
            self.train_target = train_targ
            self.train_classifiers()

    def train_classifiers(self):
        """ Trains the classifiers being used.  Modify this to introduce other classifiers """

        #self.train_classifier("1-nn", "1nn", KnnClassifier(k=1))
        #self.train_classifier("AdaBoost", "bdt",  AdaBoostClassifier(DecisionTreeClassifier(max_depth=8),
         #                        algorithm="SAMME", n_estimators=200))
        self.train_classifier("Random Forest", "rf", RandomForestClassifier(n_estimators=500, max_depth=18, n_jobs=-1))
        #self.train_classifier("SVM w/ RBF kernel", "rbf_svm", svm.SVC(kernel='rbf'))

    def make_lg(self, output, inkml, dirname):
        # fill in the inkmls with this output decision
        for i in range(len(output)):
            inkml_file, symbol = inkml[i]  # inkml is tuple of (inkml_file, symbol)
            inkml_file.class_decisions[symbol.num_in_inkml] = output[i]
        # now write each inkml out
        for inkml_file in inkml:
            inkml_file[0].print_it(dirname, self.grammar)

    def train_classifier(self, name, shorthand, model):
        print("** Training " + name + " **")
        model.fit(self.train_data, self.train_target)
        if not os.path.exists(self.param_dir):
            os.makedirs(self.param_dir)
        filename = os.path.join(self.param_dir, shorthand + ".pkl")
        if shorthand == "1nn":
            with open(filename, 'wb') as f:
                pickle.dump(model, f, pickle.HIGHEST_PROTOCOL)
        else:
            joblib.dump(model, filename)
        out = model.predict(self.train_data)
        self.make_lg(out, self.inkml, os.path.join(self.outdir, "train", shorthand))
        self.classifiers.append((name, shorthand, model))
        if self.verbose == 1:
            self.print_confusion(self.train_target, out)

    def eval(self, feature_set, num_traces):
        # the model is stored in a tuple along with its name
        model_temp = self.classifiers[0][2]
        outprob = model_temp.predict_proba(feature_set)
        max_prob = -1
        max_class = ""
        model_class_list = model_temp.classes_
        for i in range(len(outprob[0])):  # outprob returns list
            if outprob[0][i] > max_prob:
                max_prob = outprob[0][i]
                max_class = model_class_list[i]
        return max_class, math.log(max_prob)*num_traces
        
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

    def load_saved_classifier(self, param_loc, model):
        """ this loads the saved parameters from the last training of the system """
        file = os.path.join(param_loc, model)
        if model == "1nn.pkl":
            with open(file, 'rb') as handle:
                clf = pickle.load(handle)
        else:
             clf = joblib.load(file)
        name = model[:-4]  # gets rid of .pkl
        self.classifiers = [("Loaded model " + name, name+"_unpickled", clf)]