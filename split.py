import random
import scipy.stats
import numpy as np
import operator

class Split():
    """
    This class splits the data into a training a testing set
    """
    split_percent = 0.7
    threshold = 0
    iterations = 100
    k = 20

    def __init__(self, inkmllist, num_classes):

        self.train = []
        self.test = []
        #need to avoid k being larger than sample size, in that case it becomes int(min sample size/2)
        Split.k = int(min(min(len(self.train), len(self.test))/2, Split.k))
        self.num_classes = num_classes
        # make a purely random split
        for item in inkmllist:
            if random.random() <= 0.7:
                self.train.append(item)
            else:
                self.test.append(item)

    def optimize_kl(self):
        self.optimize(scipy.stats.entropy, operator.gt, Split.threshold, "KL Divergence")

    def optimize_cosine(self):
        # want to maximize the cosine similarity
        self.optimize(self.cosine, operator.lt, 1-Split.threshold, "Cosine similarity")

    def optimize(self, similarity_fn, cmp, threshold, name):

        # Iteratively increase similarity metric until we are below threshold or at given number of iterations
        pk = self.calc_distr(self.train)
        qk = self.calc_distr(self.test)
        start_s = s = similarity_fn(pk, qk)
        i = 0
        while cmp(s, threshold) and i < Split.iterations:
            # randomly sample swaps to make from train and test
            best_s = s
            best_train = self.train
            best_test = self.test
            train_swaps = random.sample(self.train, Split.k)
            test_swaps = random.sample(self.test, Split.k)
            for i in range(Split.k):
                new_pk, new_qk = self.update_distr(pk, train_swaps[i], qk, test_swaps[i])
                new_s = similarity_fn(new_pk, new_qk)
                # if cmp is less than, you want to maximize, and cmp greater than you want to minimize
                # so it is always the negation of cmp that determines a better state
                if not cmp(new_s, best_s):
                    best_s = new_s
                    best_train, best_test = self.make_new_distr(train_swaps[i], test_swaps[i])
            # after trying the k swaps keep the best one
            self.train = best_train
            self.test = best_test
            s = best_s
            i += 1
        print("Applied", name, "with starting value of", start_s, "and ending value", s, "after", i, "iterations")
        print("Training distribution")
        self.print_distr(self.calc_distr(self.train))
        print("Counts")
        self.print_distr(self.calc_distr(self.train), normalized=False)
        print("Testing distribution")
        self.print_distr(self.calc_distr(self.test))
        print("Counts")
        self.print_distr(self.calc_distr(self.test), normalized=False)

    def calc_distr(self, inkmllist):
        distr = [0]*self.num_classes
        for eqn in inkmllist:
            for symbol in eqn.symbolList:
                distr[symbol.label_index] += 1
        return distr

    def make_new_distr(self, swap_train, swap_test):
        new_train = self.train[:]
        new_test = self.test[:]
        i = self.train.index(swap_train)
        j = self.test.index(swap_test)
        new_train[i] = swap_test
        new_test[j] = swap_train
        return new_train, new_test

    @staticmethod
    def cosine(pk, qk):
        """
        Calculate the cosine similarity of two distributions for given probability values.
        This routine will normalize `pk` and `qk` if they don't sum to 1.
        """
        pk = np.array(pk)
        qk = np.array(qk)
        if len(qk) != len(pk):
            raise ValueError("qk and pk must have same length.")
        return pk.dot(qk) / (np.linalg.norm(pk) * np.linalg.norm(qk))

    @staticmethod
    def update_distr(pk, pk_swap, qk, qk_swap):
        new_pk = pk[:]
        new_qk = qk[:]
        for symbol in pk_swap:
            new_pk[symbol.label_index] -= 1
            new_qk[symbol.label_index] += 1
        for symbol in qk_swap:
            new_pk[symbol.label_index] += 1
            new_qk[symbol.label_index] -= 1
        return new_pk, new_qk

    @staticmethod
    def print_distr(distr, normalized=True):
        norm = sum(distr) if normalized else 1
        print("[", end="")
        for i in range(len(distr)):
            if i < len(distr) - 1:
                print("{:.2f}".format(distr[i]/norm), end=",")
            else:
                print("{:.2f}".format(distr[i]/norm), end="]\n")
