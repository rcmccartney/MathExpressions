__author__ = 'mccar_000'
import matplotlib.pyplot as plt

class FeatureExtraction():
    """
    Takes in a train and test set of Inkml and produces
    a 2D array of features and a 1D array of output classes
    """

    def __init__(self, train, test, verbose):
        self.train = train
        self.test = test
        self.verbose = verbose
        self.x = []  # 2d array of features
        self.y = []  # 1d array of class values

    def get_fake_data(self):
        """
        used to test the flow of the system
        """
        x = [[1, 2, 3, 4], [10, 9, 8, 7]]
        y = [0, 1]
        return x,y
        
    #scale all points to a 1 x 1 square boundingbox
    def rescale_points(self, xList, yList, boundSquareLen=1):
        xMin = min(xList)
        yMin = min(yList)
        xRange = max(xList) - min(xList)
        yRange = max(yList) - min(yList)
        if xRange > yRange:
            divScale = xRange/float(boundSquareLen)
        else:
            divScale = yRange/float(boundSquareLen)
        xTrans = [(x-xMin)/divScale for x in xList]
        yTrans = [(y-yMin)/divScale for y in yList]
        return xTrans, yTrans
                
    #this is copied from Kenny's code
    def get_aspect_ratio(self, train, test, verbose):
        plt.ion()
        plt.show()
        
        self.train = train
        self.test = test
        self.verbose = verbose
        
        x = []
        y = []
        for inkmlFile in self.train:
            for symbol in inkmlFile.symbol_list:
                min_x = 1
                max_x = -1
                min_y = 1
                max_y = -1
                for trace in symbol.trace_list:
                    t_minX, t_maxX, t_minY, t_maxY = trace.getBoundaries()
                    min_x = min(t_minX, min_x)
                    max_x = max(t_maxX, max_x)
                    min_y = min(t_minY, min_y)
                    max_y = max(t_maxY, max_y)
                w = (max_x - min_x)
                h = (max_y - min_y)
                ratio = w / h
                x.append([ratio])
                y.append([symbol.label_index])
        return x,y

    #right now this is outputting a single list of symbols - not sure how to handle the training and test sets
  
    def get_number_strokes(self, train, test, verbose):
        self.train = train
        self.test = test
        self.verbose = verbose
        
        x = []
        y = []
        for inkmlFile in self.train:
            for symbol in inkmlFile.symbol_list:
                x.append([len(symbol.trace_list)])
                y.append([symbol.label_index])
        return x,y
        