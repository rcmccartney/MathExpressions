from pybrain.datasets import ClassificationDataSet, SequenceClassificationDataSet
from pybrain.utilities import percentError
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.structure.modules import LSTMLayer, SoftmaxLayer, SigmoidLayer, ReluLayer, TanhLayer
from pybrain.supervised import RPropMinusTrainer
from pybrain.tools.validation import testOnSequenceData
from pybrain.tools.shortcuts import buildNetwork
from pylab import plot, hold, show


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
        print(results)
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
            data.addSample(x[i], y[i])
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
