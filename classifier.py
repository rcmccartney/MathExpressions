__author__ = 'mccar_000'


class Classifier():
    """ This class is a wrapper around whatever classifiers are implemented for the inkml classification """

    def __init__(self, data, target, param_file, testing, verbose):
        """
        :param data: the data to operate on
        :param target: target outputs for classification
        :param param_file: the parameters to use if testing, or the location to save for training
        :param testing: boolean whether we are testing the data or training on it
        :param verbose: boolean to print verbose output for debugging
        :return:
        """
        self.data = data
        self.target = target
        self.param_file = param_file
        self.testing = testing
        self.verbose = verbose


def get_saved_params():
    # :TODO load saved classifier parameters
    """ this loads the saved parameters from the last training of the system """
    return None
