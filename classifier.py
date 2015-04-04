__author__ = 'mccar_000'

import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
<<<<<<< Updated upstream
from classifiers.KnnClassifier import KnnClassifier
=======
from classifiers.KnnClassifier import *

>>>>>>> Stashed changes

class Classifier():
    """ This class is a wrapper around whatever classifiers are implemented for the inkml classification """

    def __init__(self, train_data, train_targ, test_data, test_targ, param_file, testing, grammar, verbose):
        """
        :param data: the data to operate on
        :param target: target outputs for classification
        :param param_file: the parameters to use if testing, or the location to save for training
        :param testing: boolean whether we are testing the data or training on it
        :param verbose: boolean to print verbose output for debugging
        """
        self.train_data = train_data
        self.train_target = train_targ
        self.param_file = param_file
        self.testing = testing
        self.verbose = verbose
        self.grammar = grammar

<<<<<<< Updated upstream
    def knn(self, k, test_data, test_target=None):
        c = KnnClassifier(self.data, self.target)
=======
    def knn(self):
        c = KnnClassifier(self.train_data, self.train_target, len(self.grammar))
>>>>>>> Stashed changes
        print("** 1-nn **")
        c.k_near(k, test_data, test_target)
        print_confusion(c.confusion, c.X.shape[0])

    @staticmethod
    def get_saved_params():
        # :TODO load saved classifier parameters
        """ this loads the saved parameters from the last training of the system """
        return None


def plot_data(data, target, num_classes, type="feat", f1=0, f2=1, figure_no=1):
    """ Plots the data onto any figure number supplied using t-SNE or PCA if desired """

    x = np.asarray(data)
    y = np.asarray(target)
    k = list(colors.cnames.keys())
    plt.figure(figure_no)
    ax = plt.subplot(121)

    if type == "tsne":
        plt.suptitle("Plotted with T-SNE algorithm for dimensionality reduction")
        model = TSNE(n_components=2, random_state=0)
        feat = model.fit_transform(x)
    elif type == "pca":
        plt.suptitle("Plotted with PCA algorithm for dimensionality reduction")
        feat = PCA(n_components=2).fit_transform(x)
    else:  # type=="feat"
        plt.suptitle("Plotted using features " + str(f1) + " and " + str(f2))
        feat = x[:, [f1, f2]]

    mins = np.amin(feat, axis=0)
    maxs = np.amax(feat, axis=0)
    ax.set_xlim([mins[0], maxs[0]])
    ax.set_ylim([mins[1], maxs[1]])
    # separate the classes for plotting by color
    for i in range(num_classes):
        class_data = feat[np.where(y == i)]
        ax.scatter(class_data[:, 0], class_data[:, 1], s=80, color=k[i])
    add_color(k, num_classes, figure_no)
    plt.show()


def add_color(colorlist, num, figure_no):
    """ Plots the colors being used along with a class label """""
    plt.figure(figure_no)
    ax = plt.subplot(122)
    ratio = 1.0 / 3.0
    count = math.ceil(math.sqrt(num))
    x_count = count * ratio
    y_count = count / ratio
    x = 0
    y = 0
    w = 1 / x_count
    h = 1 / y_count
    for i in range(num):
        pos = (x / x_count, y / y_count)
        ax.add_patch(patches.Rectangle(pos, w, h, color=colorlist[i]))
        ax.annotate("class " + str(i), xy=pos)
        if y >= y_count-1:
            x += 1
            y = 0
        else:
            y += 1


def print_confusion(conf_mat):
    """
    Prints confusion matrix in nice formatting
    """
    conf_mat = np.asarray(conf_mat)
    print("Classification rate: {:.2f}%".format(100*(np.trace(conf_mat) / np.sum(conf_mat))))
    print("Targ/Out  0", end=" ")
    for i in range(1, conf_mat.shape[0]):
        print("{:9d}".format(i), end=" ")
    for i in range(conf_mat.shape[0]):
        print("\n", i, end=" ")
        for j in range(conf_mat.shape[1]):
            print("{:9d}".format(conf_mat[i, j]), end=" ")
    print()


def test():
    data = np.load("classifiers/data.npy")
    print(data)
    x = np.asarray(data[:, :-1])
    y = np.asarray(data[:, -1])
    plot_data(x, y, 2, type="pca")
    plot_data(x, y, 2)


if __name__ == "__main__":
    test()