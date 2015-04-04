__author__ = 'Rob McCartney'

import numpy as np
import scipy.stats


class KnnClassifier():

    def __init__(self, k=1):
        """ Initialize paramters for the classifier
        """
        self.k = k
        self.x = None
        self.y = None

    def fit(self, data, target):
        self.x = np.asarray(data)
        self.y = np.asarray(target)

    def predict(self, test):
        """
        Performs K nearest neighbor classification for any choice of K set in constructor
        :return out : the predicted classes for the test_data
        """
        test_data = np.asarray(test)
        assert self.x is not None and self.y is not None, "You must train the classifier before testing"
        results = []
        for i in range(test_data.shape[0]):
            m = self.x - test_data[i]
            # dist holds the Euclidean distance to every training point
            dist = np.sum(m*m, 1)
            # this call uses a quickselect algo to find k-smallest
            ind = np.argpartition(dist, self.k)[:self.k]
            # take the class present the most among the k closest
            out = int(scipy.stats.mode(self.y[ind], axis=None)[0])
            results.append(out)
        return results