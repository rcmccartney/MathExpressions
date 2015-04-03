__author__ = 'Rob McCartney'

import numpy as np
import matplotlib.pyplot as plt


class Classifier:

    def __init__(self, data):
        """
        Chops the data into X and Y matrices, and sticks 1s into first column of X
        :param data: Assumed to be a 2-class dataset with Target values in last column
        """
        self.X = np.ones((data.shape[0], data.shape[1]))
        self.X[:, 1:] = data[:, :-1]
        self.Y = data[:, -1]
        # used for plots
        offset = 0.2
        self.max = self.X.max(0)[1:] + offset
        self.min = self.X.min(0)[1:] - offset
        # prepare locations for background classification data, adding the column of 1's
        self.resolution = 800  # higher this is, the better the lines but longer it takes
        self.factor = 8  # this scales the background dots down so they don't drown image
        tic_x, tic_y = np.mgrid[self.min[0]:self.max[0]:800j, self.min[1]:self.max[1]:800j]
        self.background = np.ones((tic_x.ravel().shape[0], 3))
        self.background[:, 1:] = np.vstack([tic_x.ravel(), tic_y.ravel()]).T
        # set up confusion matrices
        self.confusion = [[0, 0], [0, 0]]
        self.threshold = 0.5

    def empty_confusion(self):
        self.confusion = [[0, 0], [0, 0]]

    def plot_data(self, figure_no):
        """
        Plots the data onto any figure number supplied
        :param figure_no: This changes what figure is drawn for use with multiple plots
        """
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

    def linear_regression(self, *args):
        """
        Performs least squares, calculates accuracy, plots the data and the decision boundary
        """
        # closed form solution given by linear regression
        self.beta = np.linalg.inv(self.X.T.dot(self.X)).dot(self.X.T).dot(self.Y)
        # this classifies the data and turns output into 0 or 1
        results = self.X.dot(self.beta)
        results = (results > self.threshold).choose(results, 1)
        results = (results <= self.threshold).choose(results, 0)
        # make confusion matrix - first index is true class, second index is predicted class
        self.empty_confusion()
        for i in range(int(self.Y.size)):
            self.confusion[int(self.Y[i])][int(results[i])] += 1
        # classify and print the background pixels - first lower the resolution by factor to keep it clean
        back = self.background.reshape(self.resolution, self.resolution, 3)[::self.factor, ::self.factor, :]
        back = back.reshape(self.resolution/self.factor*self.resolution/self.factor, 3)
        results = back.dot(self.beta)
        r_c0 = back[np.where(results <= self.threshold)]
        r_c1 = back[np.where(results > self.threshold)]
        plt.figure(args[0])
        plt.scatter(r_c0[:, 1], r_c0[:, 2], marker='.', edgecolors='none',  s=6, c='blue')
        plt.scatter(r_c1[:, 1], r_c1[:, 2], marker='.', edgecolors='none', s=6, c='orange')
        # print the decision boundary - this formula is just basic line using two points
        x2_min = (self.threshold - self.beta[0] - self.beta[1]*self.min[0])/self.beta[2]
        x2_max = (self.threshold - self.beta[0] - self.beta[1]*self.max[0])/self.beta[2]
        plt.plot([self.min[0], self.max[0]], [x2_min, x2_max], 'k', linewidth=2)

    def k_near(self, figure_no, k):
        """
        Performs K nearest neighbor classification for any choice of K
        :param figure_no: figure to plot onto
        :param k: the number of neighbors that vote on classification decision
        """
        self.empty_confusion()
        data = self.X[:, 1:]  # get rid of the column of 1s
        for i in range(int(self.Y.size)):
            M = data - data[i]
            dist = np.sum(M*M, 1)  # dist holds the Euclidean distance to every other point
            ind = np.argpartition(dist, k)[:k]  # this call uses a quickselect algo to find k-smallest
            out = np.around(np.sum(self.Y[ind]) / k)
            self.confusion[int(self.Y[i])][int(out)] += 1

        # do the same for the background pixels
        back = self.background[:, 1:]
        classes = np.zeros(self.resolution*self.resolution)
        # these will hold the decision boundary points
        x = []
        y = []
        for i in range(int(back.shape[0])):
            M = data - back[i]
            dist = np.sum(M*M, 1)  # dist holds the Euclidean distance to every other point
            ind = np.argpartition(dist, k)[:k]  # this call uses a quickselect algo to find k-smallest
            classes[i] = np.around(np.sum(self.Y[ind]) / k)
            # make sure we are still in the same column and that the class changed
            if i > 0 and classes[i] != classes[i-1] and back[i][0] == back[i-1][0]:
                x.append(back[i][0])
                y.append(back[i][1])
            # now do it for rows
            if i > self.resolution and classes[i] != classes[i-self.resolution] \
                    and back[i][1] == back[i-self.resolution][1]:
                x.append(back[i][0])
                y.append(back[i][1])

        #reduce resolution for printing background
        classes_reduced = classes.reshape(self.resolution, self.resolution)[::self.factor, ::self.factor]
        classes_reduced = classes_reduced.reshape(self.resolution/self.factor*self.resolution/self.factor, 1)
        back_reduced = back.reshape(self.resolution, self.resolution, 2)[::self.factor, ::self.factor, :]
        back_reduced = back_reduced.reshape(self.resolution/self.factor*self.resolution/self.factor, 2)
        r_c0 = back_reduced[np.where(classes_reduced <= self.threshold), :][0]
        r_c1 = back_reduced[np.where(classes_reduced > self.threshold), :][0]
        plt.figure(figure_no)
        plt.scatter(r_c0[:, 0], r_c0[:, 1], marker='.', edgecolors='none',  s=6, c='blue')
        plt.scatter(r_c1[:, 0], r_c1[:, 1], marker='.', edgecolors='none', s=6, c='orange')
        plt.scatter(x, y, marker='.', edgecolors='none', s=5, c='k')

    def print_confusion(self):
        """
        Prints confusion matrix in nice formatting
        """
        print("Targ/Out  0 %9d" % 1, end=" ")
        for i in range(len(self.confusion)):
            print("\n", i, end=" ")
            for j in range(len(self.confusion[0])):
                print("%9d" % self.confusion[i][j], end=" ")
        print()


def pipeline(c, name, func, *args):
    """
    The common functionality for every algorithm used, including classifying and printing to console
    :param c: classifier object
    :param name: name of algorithm being used for display to user
    :param func: the function to call that matches the name parameter
    :param args: includes things like the figure to draw to and the number K to use for k-nn
    """
    print("**" + name + " Classifier**")
    func(*args)
    print("Classification rate: {:.2f}%".format(100*(c.confusion[0][0] + c.confusion[1][1]) / c.X.shape[0]))
    print("Confusion Matrix:")
    c.print_confusion()
    c.plot_data(args[0])
    print()


def main():
    data = np.load("data.npy")
    c = Classifier(data)
    for tup in [("Linear", c.linear_regression, (0)), ("1-nn", c.k_near, 1, 1), ("15-nn", c.k_near, 2, 15)]:
        pipeline(c, tup[0], tup[1], tup[2], tup[-1])

if __name__ == "__main__":
    main()