__author__ = 'Rob McCartney'

import numpy as np
import scipy.stats


class KnnClassifier():

    def __init__(self, data, Y=None, classes=2):
        """
        Chops the data into X and Y matrices if necessary
        :param data: input data, assumes target values in last column unless separate Y vector provided
        :param Y: Separate target output vector
        """
        if Y is not None:
            self.X = np.asarray(data)
            self.Y = np.asarray(Y)
        else:
            self.X = np.asarray(data[:, :-1])
            self.Y = np.asarray(data[:, -1])
        self.numclasses = classes
        # set up confusion matrice
        self.confusion = self.empty_confusion()

    def empty_confusion(self):
        """ Makes an empty confusion matrix for numclasses """
        conf = []
        for i in range(self.numclasses):
            conf.append([0]*self.numclasses)
        return conf

    def k_near(self, k):
        """
        Performs K nearest neighbor classification for any choice of K
        :param k: the number of neighbors that vote on classification decision
        """
        self.confusion = self.empty_confusion()
        data = self.X
        for i in range(int(self.Y.size)):
            M = data - data[i]
            # dist holds the Euclidean distance to every other point
            dist = np.sum(M*M, 1)
            # this call uses a quickselect algo to find k-smallest
            ind = np.argpartition(dist, k)[:k]
            # take the class present the most among the k closest
            out = scipy.stats.mode(self.Y[ind], axis=None)
            self.confusion[int(self.Y[i])][int(out[0])] += 1


def test():
    from classifier import print_confusion
    data = np.load("data.npy")
    c = KnnClassifier(data)
    print("** 1-nn **")
    c.k_near(1)
    print_confusion(c.confusion, c.X.shape[0])
    print("** 15-nn **")
    c.k_near(15)
    print_confusion(c.confusion, c.X.shape[0])

if __name__ == "__main__":
    test()