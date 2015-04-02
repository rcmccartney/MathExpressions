import random
import scipy.stats
import numpy as np
import operator

class Split():
    """
    This class splits the data into a training a testing set
    """
    split_percent = 0.7
    threshold = 0.001
    iterations = 100

    def __init__(self, inkmllist, grammar):

        self.train = []
        self.test = []
        self.num_classes = len(grammar)
        self.grammar = grammar
        # make a purely random split
        for item in inkmllist:
            if random.random() <= 0.7:
                self.train.append(item)
            else:
                self.test.append(item)
        # set up number of splits to be half the smaller set of data
        self.splits = int(min(len(self.train), len(self.test)) / 2)

    def optimize_kl(self):
        self.optimize(scipy.stats.entropy, operator.gt, Split.threshold, "KL Divergence")

    def optimize_cosine(self):
        # want to maximize the cosine similarity
        self.optimize(self.cosine, operator.lt, 1-Split.threshold, "Cosine similarity")

    def optimize(self, similarity_fn, cmp, threshold, name):

        # Iteratively increase similarity metric until we are below threshold or at given number of iterations
        pk = self.calc_distr(self.train)
        qk = self.calc_distr(self.test)
        start_s = similarity_fn(pk, qk)
        best_s = start_s
        best_train = self.train
        best_test = self.test
        iterations = 0
        while cmp(best_s, threshold) and iterations < Split.iterations:
            # randomly sample swaps to make from train and test
            train_swaps = random.sample(self.train, self.splits)
            test_swaps = random.sample(self.test, self.splits)
            for i in range(self.splits):
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
            iterations += 1
        print("Applied", name, "with starting value of", start_s, "and ending value", best_s, "after", iterations, "iterations")
        print("Training set contains", len(self.train), "instances and test set contains", len(self.test), "instances")
        print("Gram : ", end="")
        self.print_grammar()
        print("Train: ", end="")
        self.print_distr(self.calc_distr(self.train))
        print("Count: ", end="")
        self.print_distr(self.calc_distr(self.train), normalized=False)
        print("Test : ", end="")
        self.print_distr(self.calc_distr(self.test))
        print("Count: ", end="")
        self.print_distr(self.calc_distr(self.test), normalized=False)

    def calc_distr(self, inkmllist):
        distr = [0]*self.num_classes
        for eqn in inkmllist:
            for symbol in eqn.symbol_list:
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

    def print_grammar(self):
        print("[ ", end="")
        gr = sorted(self.grammar, key=self.grammar.get)
        for i in range(len(self.grammar)):
            if i < len(self.grammar) - 1:
                print("{0:>4}".format(gr[i]), end=", ")
            else:
                print("{0:>4}".format(gr[i]), end="]\n")

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
        for symbol in pk_swap.symbol_list:
            new_pk[symbol.label_index] -= 1
            new_qk[symbol.label_index] += 1
        for symbol in qk_swap.symbol_list:
            new_pk[symbol.label_index] += 1
            new_qk[symbol.label_index] -= 1
        return new_pk, new_qk

    @staticmethod
    def print_distr(distr, normalized=True):
        if normalized:
            norm = sum(distr)
            formatting = "{:.2f}"
        else:
            norm = 1
            formatting = "{:4.0f}"
        print("[ ", end="")
        for i in range(len(distr)):
            if i < len(distr) - 1:
                print(formatting.format(distr[i]/norm), end=", ")
            else:
                print(formatting.format(distr[i]/norm), end="]\n")