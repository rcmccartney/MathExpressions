__author__ = 'mccar_000'

import numpy as np
import scipy.interpolate as sp
import matplotlib.pyplot as plt
import math
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
    def rescale_and_resample(trace_list, bound_square_len=1, alpha=0.01):
        """
        this method rescales and centers all points to a bounding box of bound_square_length
        """
        xmin = ymin = float("inf")
        xmax = ymax = float("-inf")
        for trace in trace_list:
            if min(trace.x) < xmin: xmin = min(trace.x)
            if max(trace.x) > xmax: xmax = max(trace.x)
            if min(trace.y) < ymin: ymin = min(trace.y)
            if max(trace.y) > ymax: ymax = max(trace.y)
        xrange = xmax - xmin
        yrange = ymax - ymin
        div_scale = max(xrange, yrange)
        all_x = []
        all_y = []
        if div_scale > 0:
            for trace in trace_list:
                new_x = [bound_square_len*(0.5*(div_scale - xmin - xmax) + x)/div_scale for x in trace.x]
                new_y = [bound_square_len*(0.5*(div_scale - ymin - ymax) + y)/div_scale for y in trace.y]
                xlist, ylist = FeatureExtraction.resample_points_const_dist(new_x, new_y, alpha)
                all_x.extend(xlist)
                all_y.extend(ylist)
        else:
            all_x = [bound_square_len/2]
            all_y = [bound_square_len/2]
        return all_x, all_y

    @staticmethod
    def resample_points_const_time(xlist, ylist, mult_increase=200):
        f1 = sp.interp1d(range(0, len(xlist)), xlist, kind='linear')
        f2 = sp.interp1d(range(0, len(ylist)), ylist, kind='linear')
        new_tseries = np.linspace(0, len(xlist)-1, len(xlist)*mult_increase)
        return f1(new_tseries), f2(new_tseries)

    @staticmethod
    def resample_points_const_dist(xlist, ylist, alpha=0.01):
        acc_len = [0.0]
        for i in range(1, len(xlist)):
            li = acc_len[-1] + math.sqrt(math.pow((xlist[i]-xlist[i-1]), 2) + math.pow((ylist[i]-ylist[i-1]), 2))
            acc_len.append(li)
        m = math.floor(acc_len[-1]/alpha)
        xlist_new = [xlist[0]]
        ylist_new = [ylist[0]]
        j = 1
        for p in range(1, (m-2)):
            while acc_len[j] < p*alpha:
                j += 1
            c = (p*alpha - acc_len[j-1]) / (acc_len[j] - acc_len[j-1])
            xlist_new.append(xlist[j-1] + (xlist[j]-xlist[j-1])*c)
            ylist_new.append(ylist[j-1] + (ylist[j]-ylist[j-1])*c)
        xlist_new.append(xlist[-1])
        ylist_new.append(ylist[-1])
        return xlist_new, ylist_new
        
    @staticmethod
    def convert_to_image(trace_list, pixel_axis=20):
        x, y = FeatureExtraction.rescale_and_resample(trace_list, bound_square_len=pixel_axis)
        x_res_np = np.around(np.array(x))
        y_res_np = np.around(np.array(y))
        image_mat = np.zeros([pixel_axis+1, pixel_axis+1])
        image_mat[y_res_np.astype(int), x_res_np.astype(int)] = 1
        return image_mat

    @staticmethod
    def convert_and_plot(trace_list, pixel_axis=20):
        trace_mat = FeatureExtraction.convert_to_image(trace_list, pixel_axis)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_aspect('equal')
        plt.imshow(trace_mat)
        plt.show()
        return trace_mat

    def get_aspect_ratio(self, symbol, verbose):        
        xMin, xMax, yMin, yMax = float("inf"),float("-inf"),float("inf"),float("-inf")
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
    
    def get_mean_x(self, xtrans, verbose):
        x = [sum(xtrans)/float(len(xtrans))]
        return x
        
    def get_mean_y(self, ytrans, verbose):
        x = [sum(ytrans)/float(len(ytrans))]
        return x
        
    def get_cov_xy(self, xtrans, ytrans, verbose):
        cov = np.cov(xtrans,ytrans)
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
                xtrans,ytrans = self.rescale_and_resample(symbol.trace_list)
                x = []
                x.extend(self.get_number_strokes(symbol,verbose))
                x.extend(self.get_cov_xy(xtrans,ytrans,verbose))
                x.extend(self.get_mean_x(xtrans,verbose))
                x.extend(self.get_mean_y(ytrans,verbose))
                x.extend(self.get_aspect_ratio(symbol,verbose))
                x_grid.append(x)
                y_true_class.append(symbol.label_index)
                inkml_file_ref.append([inkml_file, symbol.labelXML])
        return x_grid,y_true_class,inkml_file_ref