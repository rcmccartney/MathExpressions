__author__ = 'mccar_000'

import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA


class Classifier():
    """ This class is a wrapper around whatever classifiers are implemented for the inkml classification """

    def __init__(self, data, target, param_file, testing, verbose):
        """
        :param data: the data to operate on
        :param target: target outputs for classification
        :param param_file: the parameters to use if testing, or the location to save for training
        :param testing: boolean whether we are testing the data or training on it
        :param verbose: boolean to print verbose output for debugging
        :return:
        """
        self.data = data
        self.target = target
        self.param_file = param_file
        self.testing = testing
        self.verbose = verbose

    def knn(self):
        c = KnnClassifier(self.data, self.target)
        print("** 1-nn **")
        c.k_near(1)
        print_confusion(c.confusion, c.X.shape[0])

    @staticmethod
    def get_saved_params():
        # :TODO load saved classifier parameters
        """ this loads the saved parameters from the last training of the system """
        return None


def plot_data(X, type="tsne", figure_no=1):
    """ Plots the data onto any figure number supplied using t-SNE or PCA if desired """

    if type == "tsne":
        model = TSNE(n_components=2, random_state=0)
        X = model.fit_transform(self.X)
    elif type == "pca":
        X = PCA(n_components=2).fit_transform(X)


    # separate the classes for plotting
    data_c0 = self.X[np.where(self.Y == 0)]
    data_c1 = self.X[np.where(self.Y == 1)]
    plt.figure(figure_no)
    plt.scatter(data_c0[:, 1], data_c0[:, 2], s=80, facecolors='none', edgecolors='blue', label="Class 0")
    plt.scatter(data_c1[:, 1], data_c1[:, 2], s=80, facecolors='none', edgecolors='orange', label="Class 1")
    plt.xlabel("x1")
    plt.xlim([self.min[0], self.max[0]])
    plt.ylabel("x2")
    plt.ylim([self.min[1], self.max[1]])
    # Place a legend above this legend, expanding itself to fully use the given bounding box.
    plt.legend(scatterpoints=1, bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    plt.show()


def print_confusion(conf_mat, num_elems):
    """
    Prints confusion matrix in nice formatting
    """
    conf_mat = np.asarray(conf_mat)
    print("Classification rate: {:.2f}%".format(100*(np.trace(conf_mat) / num_elems)))
    print("Targ/Out  0", end=" ")
    for i in range(1, conf_mat.shape[0]):
        print("{:9d}".format(i), end=" ")
    for i in range(conf_mat.shape[0]):
        print("\n", i, end=" ")
        for j in range(conf_mat.shape[1]):
            print("{:9d}".format(conf_mat[i, j]), end=" ")
    print()