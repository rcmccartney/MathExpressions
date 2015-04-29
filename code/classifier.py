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
from code.randForest.forest import Forest
from code.randForest.AtrocityEntropyFn import *

class Classifier():
    """ This class is a wrapper around whatever classifiers are implemented for the inkml classification """

    def __init__(self, outdir=None, train_data=None, train_targ=None, grammar=None,
                 inkml=None, param_dir=None, model="rf", testing=False):
        """
        """
        self.grammar = grammar
        self.inkml = inkml
        self.classifiers = []
        self.outdir = outdir
        self.param_dir = param_dir
        self.model = model[:-4]
        if testing:
            self.load_saved_classifier(param_dir, self.model)
        else:
            self.train_data = train_data
            self.train_target = train_targ
            self.train_classifiers()

    def train_classifiers(self):
        """ Trains the classifiers being used.  Modify this to introduce other classifiers """
        if self.model == "1-nn":
            self.train_classifier("1-nn", "1nn", KnnClassifier(k=1))
        elif self.model == "bdt":
            self.train_classifier("AdaBoost", "bdt",
                                  AdaBoostClassifier(DecisionTreeClassifier(max_depth=8),
                                                     algorithm="SAMME", n_estimators=200))
        elif self.model == "rf":
            self.train_classifier("Random Forest", "rf",
                                  Forest(depthlimit=18, weak_learner=AtrocityEntropyFn(), bagging=True,
                                         numclasses=len(self.grammar)))
        else:  # svm
            self.train_classifier("SVM w/ RBF kernel", "rbf_svm", svm.SVC(kernel='rbf'))

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
        with open(filename, 'wb') as f:
            joblib.dump(model, f, compress=3)
        out = model.predict(self.train_data)
        self.make_lg(out, self.inkml, os.path.join(self.outdir, "train", shorthand))
        self.classifiers.append((name, shorthand, model))
        self.print_confusion(self.train_target, out)

    '''This limits evaluated sets to be length 5 or fewer, for the interests of executtion time'''
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

    def print_confusion(self, target, out, print_conf=False):
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
        if print_conf:
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
        clf = joblib.load(file)
        name = model[:-4]  # gets rid of .pkl
        self.model = name
        self.classifiers = [("Loaded model " + name, name+"_unpickled", clf)]