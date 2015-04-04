__author__ = 'mccar_000'
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as sp

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
                
    def resample_points(self, xList, yList, multIncrease):
        f1 = sp.interp1d(range(0,len(xList)),xList,kind = 'linear')
        f2 = sp.interp1d(range(0,len(yList)),yList,kind = 'linear')
        
        new_tseries = np.linspace(0, len(xList)-1, len(xList)*multIncrease)
        return f1(new_tseries),f2(new_tseries)
    
    def convert_to_image(self, xList, yList, pixelAxis = 100):
        x_trans, y_trans = self.rescale_points(xList, yList, 1)
        x_res, y_res = self.resample_points(x_trans,y_trans,10)
        x_res_np = np.array(x_res)*pixelAxis
        y_res_np = np.array(y_res)*pixelAxis
        print(x_res_np.astype(int))
        print(y_res_np.astype(int))
        image_mat = np.zeros([pixelAxis+1, pixelAxis+1])
        image_mat[x_res_np.astype(int),y_res_np.astype(int)] = 1
        return image_mat
        
    
    def get_aspect_ratio(self, symbol, verbose):        
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
        x = [ratio]
        return x
    
    def get_mean_x(self, symbol, verbose):
        xTemp,yTemp = symbol.get_all_points()
        xTrans,yTrans = self.rescale_points(xTemp,yTemp)
        x = [sum(xTrans)/float(len(xTrans))]
        return x
        
    def get_mean_y(self, symbol, verbose):
        xTemp,yTemp = symbol.get_all_points()
        xTrans,yTrans = self.rescale_points(xTemp,yTemp)
        x = [sum(yTrans)/float(len(yTrans))]
        return x
        
    def get_cov_xy(self, symbol, verbose):
        xTemp,yTemp = symbol.get_all_points()
        xTrans,yTrans = self.rescale_points(xTemp,yTemp)
        cov = np.cov(xTrans,yTrans)
        x = cov.flatten().tolist()
        return x
        
    def get_number_strokes(self, symbol, verbose):
        x = [len(symbol.trace_list)]
        return x
        
    def get_feature_set(self,inkml_file_list,verbose):
        x_grid = []
        y_true_class = []
        inkml_file_ref = []
        for inkml_file in inkml_file_list:
            for symbol in inkml_file.symbol_list:
                x = []
                x.extend(self.get_number_strokes(symbol,verbose))
                x.extend(self.get_cov_xy(symbol,verbose))
                x.extend(self.get_mean_x(symbol,verbose))
                x.extend(self.get_mean_y(symbol,verbose))
                x.extend(self.get_aspect_ratio(symbol,verbose))
                
                x_grid.append(x)
                y_true_class.append(symbol.label_index)
                inkml_file_ref.append([inkml_file,symbol.labelXML])
        return x_grid,y_true_class,inkml_file_ref