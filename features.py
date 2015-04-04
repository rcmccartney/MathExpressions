__author__ = 'mccar_000'
import matplotlib.pyplot as plt
import numpy as np

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
                
    def get_aspect_ratio(self, inkmlList, verbose):        
        self.inkmlList = inkmlList
        self.verbose = verbose
        
        x = []
        y = []
        for inkmlFile in self.inkmlList:
            for symbol in inkmlFile.symbol_list:
                
                xMin, xMax, yMin, yMax = 9999,-9999,9999,-9999
                for trace in symbol.trace_list:
                    xMinTemp, xMaxTemp, yMinTemp, yMaxTemp = trace.get_boundaries()
                    xMin = min(xMin, xMinTemp)
                    xMax = max(xMax, xMaxTemp)
                    yMin = min(yMin, yMinTemp)
                    yMax = max(yMax, yMaxTemp)
                w = abs(xMax-xMin)
                h = abs(yMax-yMin)
                ratio = w/h
                x.append([ratio])
                y.append([symbol.label_index])
        return x,y
  
    def get_number_strokes(self, inkmlList, verbose):
        self.inkmlList = inkmlList
        self.verbose = verbose
        
        x = []
        y = []
        for inkmlFile in self.inkmlList:
            for symbol in inkmlFile.symbol_list:
                x.append([len(symbol.trace_list)])
                y.append([symbol.label_index])
        return x,y
    
    def get_mean_x(self, inkmlList, verbose):
        self.inkmlList = inkmlList
        self.verbose = verbose
        x=[]
        y=[]
        for inkmlFile in self.inkmlList:
            for symbol in inkmlFile.symbol_list:
                xTemp,yTemp = symbol.get_all_points()
                xTrans,yTrans = self.rescale_points(xTemp,yTemp)
                x.append([sum(xTrans)/float(len(xTrans))])
                y.append([symbol.label_index])
        return x,y
        
    def get_mean_y(self, inkmlList, verbose):
        self.inkmlList = inkmlList
        self.verbose = verbose
        x=[]
        y=[]
        for inkmlFile in self.inkmlList:
            for symbol in inkmlFile.symbol_list:
                xTemp,yTemp = symbol.get_all_points()
                xTrans,yTrans = self.rescale_points(xTemp,yTemp)
                x.append([sum(yTrans)/float(len(yTrans))])
                y.append([symbol.label_index])
        return x,y
        
    def get_cov_xy(self, inkmlList, verbose):
        self.inkmlList = inkmlList
        self.verbose = verbose
        x=[]
        y=[]
        for inkmlFile in self.inkmlList:
            for symbol in inkmlFile.symbol_list:
                xTemp,yTemp = symbol.get_all_points()
                xTrans,yTrans = self.rescale_points(xTemp,yTemp)
                cov = np.cov(xTrans,yTrans)
                x.append(cov.flatten().tolist())
                y.append([symbol.label_index])
        return x,y
        
    def compose_feature_matrix(self, inkmlList, verbose):
        self.inkmlList = inkmlList
        self.verbose = verbose
        