__author__ = 'Rob McCartney'

import numpy as np
import scipy.stats


class KnnClassifier():

    def __init__(self, data, target, num_classes=2):
        """
        Chops the data into X and Y matrices if necessary
        :param data: input data, assumes target values in last column unless separate Y vector provided
        :param Y: Separate target output vector
        """
        self.X = np.asarray(data)
        self.Y = np.asarray(target)
        self.num_classes = num_classes

    def empty_confusion(self):
        """ Makes an empty confusion matrix for numclasses """
        conf = []
        for i in range(self.num_classes):
            conf.append([0]*self.num_classes)
        return conf

    def k_near(self, k, test_data, test_target=None):
        """
        Performs K nearest neighbor classification for any choice of K
        :param k: the number of neighbors that vote on classification decision
        :return out, confusion : the predicted classes for the test_data as well
        as a confusion matrix if test_target is provided
        """
        confusion = self.empty_confusion() if test_target is not None else None
        results = []
        for i in range(test_data.shape[0]):
            M = self.X - test_data[i]
            # dist holds the Euclidean distance to every training point
            dist = np.sum(M*M, 1)
            # this call uses a quickselect algo to find k-smallest
            ind = np.argpartition(dist, k)[:k]
            # take the class present the most among the k closest
            out = int(scipy.stats.mode(self.Y[ind], axis=None)[0])
            results.append(out)
            # compare to ground truth if it is available
            if test_target is not None:
                confusion[int(test_target[i])][int(out)] += 1
        return results, confusion


def test():
    from classifier import print_confusion
    data = np.load("data.npy")
    x = np.asarray(data[:, :-1])
    y = np.asarray(data[:, -1])
    c = KnnClassifier(x, y)
    print("** 1-nn **")
    results, conf = c.k_near(1, x, y)
    print_confusion(conf)
    print("** 15-nn **")
    results, conf = c.k_near(15, x, y)
    print_confusion(conf)
    print("** Testing w/o target values **")
    results, _ = c.k_near(1, x)
    print("Test", "passed" if results == list(y) else "failed")

if __name__ == "__main__":
    test()