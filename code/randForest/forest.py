__author__ = 'Robert McCartney'

from code.randForest.tree import *
import math
import random
import pickle
import numpy as np
from multiprocessing.pool import Pool


def make_tree(tree_data):
    """
    Use this function to make a tree in parallel using all cores of the machine
    :param tree_data: Tuple of (self.data_copy(), self.bag, self.bag_ratio, self.depthlimit, self.weak_learner)
    :return: Tree made by this thread
    """
    return Tree(tree_data[0], tree_data[1], tree_data[2])


class Forest(object):

    def __init__(self, depthlimit=3, weak_learner=None, bagging=False, bag_ratio=.4, default_tree_count=200,
                 numclasses=-1):
        """
        Initialize all the variables required for this random forest
        :param depthlimit: the depth allowed in a tree of the forest
        :param weak_learner: how we split the data and traverse a tree, used as a Strategy design pattern
        :param bagging: boolean to use bagging or not
        :param bag_ratio: if using bagging, what percent of the data to use
        :param default_tree_count: how many trees to train in this random forest
        :return: None
        """
        self.bagging = bagging
        self.bag_ratio = bag_ratio
        self.default_tree_count = default_tree_count
        self.trees = []
        self.error = []
        self.data = []
        self.depthlimit = depthlimit
        self.weak_learner = weak_learner
        self.numclasses = numclasses

    def fit(self, x, y):
        """
        Train the forest without saving the data
        :param x: data to use, already processed into 2D numpy array
        :param y: output values, a 1D numpy array of ints
        :param classes: list of the class decision for each row in instances
        :param numclass: number of classes in this dataset
        :return: None
        """
        y = np.asarray(y)
        # append a class decision vector such as [0, 1, 0, 0] (here is a 4 class problem) to row of data
        l = np.arange(y.size)
        out = np.zeros((y.size, self.numclasses))
        out[l, y] = 1
        out.tolist()
        x = x.tolist()
        for row in range(len(x)):
            x[row].append(out[row])
        self.data = x
        self.add_tree(iterations=self.default_tree_count)
        self.data = None

    def add_tree(self, iterations=-1):
        """
        Multi-core, fully utilizes underlying CPU to create the trees
        of the forest and stores them into the forest's list of trees
        :param iterations: number of trees to make, -1 means use default setting
        :return: None
        """
        print("Adding trees:", iterations)
        if iterations == -1:
            iterations = self.default_tree_count
        #########################
        # MULTI THREADED
        ########################
        pool = Pool()  # creates multiple processes equal to cores in machine
        outputs = pool.map(make_tree, [(self.data_copy(), self.depthlimit, self.weak_learner)
                                       for _ in range(iterations)])
        pool.close()
        pool.join()
        self.trees.extend(outputs)  # get the trees created and store them

    def data_copy(self):
        """
        Gives each thread its own copy of the data
        :return: thread-local copy of the data to make a tree from
        """
        if self.bagging:
            return [self.data[random.randint(0, len(self.data)-1)] for _ in range(int(self.bag_ratio*len(self.data)))]
        else:
            return self.data[:]

    def predict_proba(self, test_data):
        """
        Averages the distribution of every tree in the forest to calc final distribution
        :param instance: that you want to classify using this forest
        :return: distribution of class decisions, representing a confidence percentage
        """
        # use a simple average to combine distributions
        totals = []
        tot_trees = len(self.trees)
        for instance in test_data:
            distr = [0 for _ in range(self.numclasses)]  # create the distribution container
            for tree in self.trees:
                tree_distr = tree.get_instance_distr(instance)
                for i in range(len(distr)):
                    distr[i] += tree_distr[i]
            totals += [prob/tot_trees for prob in distr]  # this gives avg prob dist for trees
        return totals

    def __str__(self):
        """
        :return: string representation of this forest
        """
        name = ""
        for a_tree in self.trees:
            name += str(a_tree)
        return name
#end Forest class