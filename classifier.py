__author__ = 'mccar_000'

from classifiers.KnnClassifier import *
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


class Classifier():
    """ This class is a wrapper around whatever classifiers are implemented for the inkml classification """

    def __init__(self, train_data=None, train_targ=None, grammar=None, verbose=None, param_file=None):
        """
        :param param_file: the parameters to use if testing, or the location to save for training
        :param verbose: boolean to print verbose output for debugging
        """
        if param_file is not None:
            self.load_saved_classifiers()
        else:
            self.train_data = train_data
            self.train_target = train_targ
            self.grammar = grammar
            self.classifiers = []
            self.train_classifiers(verbose)

    def train_classifiers(self, verbose):
        """ Trains the classifiers being used.  Modify this to introduce other classifiers """
        print("** Training 1-nn **")
        knn = KnnClassifier(k=1)
        knn.fit(self.train_data, self.train_target)
        if verbose:
            self.print_confusion(self.train_target, knn.predict(self.train_data))
        print("** Training AdaBoost **")
        # Create and fit an AdaBoosted decision tree
        bdt = AdaBoostClassifier(DecisionTreeClassifier(max_depth=3),
                                 algorithm="SAMME", n_estimators=200)
        bdt.fit(self.train_data, self.train_target)
        if verbose:
            self.print_confusion(self.train_target, knn.predict(self.train_data))
        # Create and fit a random forest
        print("** Training Random Forest **")
        clf = RandomForestClassifier(n_estimators=10)
        clf = clf.fit(self.train_data, self.train_target)
        self.classifiers = [("1-NN", knn), ("Boosted decision trees", bdt), ("Random foresT", clf)]

    def test_classifiers(self, test_data, test_targ=None, inkml=None, outdir=None):
        """
        Tests the classifiers trained above on the testing target data.
        If target output is provided then a confusion matrix is created
        """
        for classifier in self.classifiers:
            print("Testing", classifier[0])
            out = classifier[1].predict(test_data)
            if test_targ is not None:
                self.print_confusion(test_targ, out)
            print(inkml)
            print(outdir)

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