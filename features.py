__author__ = 'mccar_000'

import numpy as np
import scipy.interpolate as sp
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter("error")


class FeatureExtraction():
    """
    Takes in a train and test set of Inkml and produces
    a 2D array of features and a 1D array of output classes
    """

    def __init__(self, verbose):
        self.verbose = verbose

    @staticmethod
    def rescale_points(xlist, ylist, bound_square_len=1):
        """
        this method rescales and centers all points to a bounding box of bound_square_length
        """
        xmin = min(xlist)
        xmax = max(xlist)
        ymin = min(ylist)
        ymax = max(ylist)
        xrange = xmax - xmin
        yrange = ymax - ymin
        div_scale = max(xrange, yrange)
        if div_scale > 0:
            x_trans = [(bound_square_len*0.5*(div_scale - xmin - xmax) + x)/div_scale for x in xlist]
            y_trans = [(bound_square_len*0.5*(div_scale - ymin - ymax) + y)/div_scale for y in ylist]
        else:
            x_trans = y_trans = [bound_square_len/2]
        return x_trans, y_trans

    @staticmethod
    def resample_points(xlist, ylist, mult_increase):
        f1 = sp.interp1d(range(0, len(xlist)), xlist, kind='linear')
        f2 = sp.interp1d(range(0, len(ylist)), ylist, kind='linear')
        new_tseries = np.linspace(0, len(xlist)-1, len(xlist)*mult_increase)
        return f1(new_tseries), f2(new_tseries)

    @staticmethod
    def convert_to_image(xlist, ylist, pixel_axis=20):
        x, y = FeatureExtraction.rescale_points(xlist, ylist)
        x, y = FeatureExtraction.resample_points(x, y, 100)
        x_res_np = np.around(np.array(x)*pixel_axis)
        y_res_np = np.around(np.array(y)*pixel_axis)
        image_mat = np.zeros([pixel_axis+1, pixel_axis+1])
        image_mat[x_res_np.astype(int), pixel_axis - y_res_np.astype(int)] = 1
        return image_mat

    @staticmethod
    def convert_and_plot(xlist, ylist, pixel_axis=20):
        trace_mat = FeatureExtraction.convert_to_image(xlist, ylist, pixel_axis)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_aspect('equal')
        plt.imshow(trace_mat)
        plt.show()
        return trace_mat

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
        if h != 0:
            ratio = w/h
        else:
            ratio = 1
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
        
    def get_feature_set(self, inkml_file_list, verbose):
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
                inkml_file_ref.append([inkml_file, symbol.labelXML])
        return x_grid,y_true_class,inkml_file_ref