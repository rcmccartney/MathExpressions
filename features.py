import random
import scipy

class Split():
    """
    This class splits the data into a training a testing set
    """
    split_percent = 0.7
    threshold = 0
    iterations = 100
    k = 20

    def __init__(self, inkmllist):

        self.train = []
        self.test = []

        # make a purely random split
        for item in inkmllist:
            if random.random() <= 0.7:
                self.train.append(item)
            else:
                self.test.append(item)

        # this calculates the KL divergence
        # and loops until we are below threshold or at number of iterations
        pk = calc_distr(self.train)
        qk = calc_distr(self.test)
        start_s = s = scipy.stats.entropy(pk, qk=qk, base=None)
        i = 0
        while s > Split.threshold and i < Split.iterations:
            # randomly sample swaps to make from train and test
            best_s = s
            best_train = self.train
            best_test = self.test
            train_swaps = random.sample(self.train, Split.k)
            test_swaps = random.sample(self.test, Split.k)
            for i in range(Split.k):
                new_pk, new_qk = update_distr(pk, qk, train_swaps[i], test_swaps[i])
                new_s = scipy.stats.entropy(new_pk, qk=new_qk, base=None)
                if new_s < best_s:
                    best_s = new_s
                    best_train, best_test = make_new_distr(self.train, self.test, train_swaps[i], test_swaps[i])
            # after trying the k swaps keep the best one
            self.train = best_train
            self.test = best_test
            s = best_s
            i += 1

        print("Applied KL divergence with starting value of", start_s, "and ending value", s, "after", i, "iterations")
        print("Training distribution")
        print_distr(self.train)
        print("Testing distribution")
        print_distr(self.test)

    @staticmethod
    def update_distr(pk, qk, train_to_swap, test_to_swaps):

