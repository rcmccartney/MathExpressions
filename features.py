__author__ = 'mccar_000'

class FeatureExtraction():
    """
    Takes in a train and test set of Inkml and produces
    a 2D array of features and a 1D array of output classes
    """

    def __init__(self, train, test):
        self.train = train
        self.test = test
        self.x = []  # 2d array of features
        self.y = []  # 1d array of class values

    def get_fake_data(self):
        """
        used to test the flow of the system
        """
        x = [[1, 2, 3, 4], [10, 9, 8, 7]]
        y = [0, 1]
        return x,y