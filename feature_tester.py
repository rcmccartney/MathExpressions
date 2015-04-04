__author__ = 'mccar_000'

import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA


class TestFeatures():
    """ This class is used to see how well the features separate the data """

    def __init__(self, data, out, grammar):
        self.plot_data(data, out, len(grammar), ptype="tsne", figure_no=1)
        self.plot_data(data, out, len(grammar), ptype="pca", figure_no=2)
        self.plot_data(data, out, len(grammar), ptype="feat", figure_no=3)

    @staticmethod
    def plot_data(data, target, num_classes, ptype="feat", f1=0, f2=1, figure_no=1):
        """ Plots the data onto any figure number supplied using t-SNE or PCA if desired """

        x = np.asarray(data)
        y = np.asarray(target)
        k = list(colors.cnames.keys())
        plt.figure(figure_no)
        ax = plt.subplot(121)

        if ptype == "tsne":
            plt.suptitle("Plotted with T-SNE algorithm for dimensionality reduction")
            model = TSNE(n_components=2, random_state=0)
            feat = model.fit_transform(x)
        elif ptype == "pca":
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
        TestFeatures.add_color(k, num_classes, figure_no)
        plt.show()

    @staticmethod
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