from pybrain.datasets import ClassificationDataSet, SequenceClassificationDataSet
from pybrain.utilities import percentError
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.structure.modules import LSTMLayer, SoftmaxLayer, SigmoidLayer, ReluLayer, TanhLayer
from pybrain.supervised import RPropMinusTrainer
from pybrain.tools.validation import testOnSequenceData
from pybrain.tools.shortcuts import buildNetwork
from pylab import plot, hold, show

import numpy as np
import scipy.stats


class KnnClassifier():

    def __init__(self, k=1):
        """ Initialize paramters for the classifier
        """
        self.k = k
        self.x = None
        self.y = None
        self.classes_ = None
        
    def fit(self, data, target):
        self.x = np.asarray(data)
        self.y = np.asarray(target)
        self.classes_ = np.asarray(target)
        
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

    def predict_proba(test, label): #return the associated score
        out_probs = []
        for i in range(len(test)):
            ave_dist = 0
            count = 0
            for j in self.y:
                if self.y[j] == label:
                    ave_dist += np.linalg.norm(self.x[j],test_data[i])
                    count += 1
            ave_dist /= count
            out_probs.append(ave_dist)
        return out_probs

class FFNeural():
    """ Uses pybrain for two neural network implementations """

    def __init__(self, numclasses):
        self.numclasses = numclasses
        self.trainer = None

    def fit(self, x, y, iteration=100):
        train_data = self.load_data(x, y, self.numclasses)
        #now build the neural network
        network = buildNetwork(train_data.indim, 30, train_data.outdim, bias=True,
                               hiddenclass=TanhLayer, outclass=SoftmaxLayer)
        network.randomize()
        # set a learning rate decay lrdecay=1.0
        trainer = BackpropTrainer(network, learningrate=0.01, dataset=train_data,
                                  momentum=0.95, batchlearning=True, weightdecay=0.0005)
        for _ in range(0, iteration, iteration//10):
            trainer.trainEpochs(iteration//10)
            trnresult = percentError(trainer.testOnClassData(), train_data['class'])
            print("Epoch: %3d" % trainer.totalepochs, "train percent error: %5.2f%%" % trnresult)
        self.trainer = trainer

    def predict(self, test_x, test_y=None):
        test_data = self.load_data(test_x, test_y, self.numclasses)
        results = self.trainer.testOnClassData(dataset=test_data)
        if test_y is not None:
            tstresult = percentError(results, test_data['class'])
            print("Test percent error: %5.2f%%" % tstresult)
        #NetworkWriter.writeToFile(network, 'output_network.xml')
        #recover with net = NetworkReader.readFrom('filename.xml')
        return results

    @staticmethod
    def load_data(x, y, numclasses):
        data = ClassificationDataSet(len(x[0]), nb_classes=numclasses)
        for i in range(len(x)):
            if y is not None:
                data.addSample(x[i], y[i])
            else:
                data.addSample(x[i], 0)  # this is for testing, output class doesn
        data._convertToOneOfMany(bounds=[0., 1.])  # changes output to vector of 0's and 1's
        return data


class LSTMNeural():
    """ Uses pybrain for two neural network implementations """

    def __init__(self, numclasses):
        self.numclasses = numclasses
        self.rnn = None

    def fit(self, x, y, iteration=100):
        train_data = self.load_data(x, y, self.numclasses)
        # construct LSTM network - note the missing output bias
        rnn = buildNetwork(train_data.indim, 5, train_data.outdim, hiddenclass=LSTMLayer,
                           outclass=SoftmaxLayer, outputbias=False, recurrent=True)
        # define a training method
        trainer = RPropMinusTrainer(rnn, dataset=train_data, verbose=False)
        # instead, you may also try
        ##trainer = BackpropTrainer( rnn, dataset=trndata, verbose=True, momentum=0.9, learningrate=0.00001 )
        # carry out the training
        for _ in range(0, iteration, iteration//10):
            trainer.trainEpochs(iteration//10)
            trnresult = 100. * (1.0-testOnSequenceData(rnn, train_data))
            print("train error: %5.2f%%" % trnresult)
        self.rnn = rnn
        # just for reference, plot the first 5 timeseries
        plot(train_data['input'][0:250, :], '-o')
        hold(True)
        plot(train_data['target'][0:250, 0])
        show()

    def predict(self, test_x, test_y=None):
        test_data = self.load_data(test_x, test_y, self.numclasses)
        tstresult = 100. * (1.0-testOnSequenceData(self.rnn, test_data))
        print("Test percent error: %5.2f%%" % tstresult)

    @staticmethod
    def load_data(x, y, numclasses):
        data = SequenceClassificationDataSet(len(x[0]), numclasses)
        for i in range(len(x)):
            data.newSequence()
            data.appendLinked(x[i], y[i])
        data._convertToOneOfMany(bounds=[0., 1.])  # changes output to vector of 0's and 1's
        return data
