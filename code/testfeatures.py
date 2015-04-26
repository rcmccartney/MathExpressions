import numpy as np
import math


def get_rowwise_crosses_maxmin(image_mat, numregions, verbose):
    numrows, numcols = image_mat.shape
    
    rowwidth = int(math.floor(numrows/numregions))
    avelist = []
    mincrosslist = []
    maxcrosslist = []
    for i in range(0,numrows,rowwidth):
        subrows = image_mat[i:i+rowwidth,:]
        ave = subrows.sum()/float(rowwidth)
        
        minindexsum = 0
        maxindexsum = 0
        for row in subrows:
            nonzero_indices = np.where(row != 0)[1]
            nonzero_indices = nonzero_indices.tolist()[0]
            if len(nonzero_indices) == 0:
                min = 0
                max = len(subrows)-1
            else:
                min = np.amin(nonzero_indices)
                max = np.amax(nonzero_indices)
            minindexsum += min
            maxindexsum += max
        minindexave = float(minindexsum)/float(len(subrows))
        maxindexave = float(maxindexsum)/float(len(subrows))
        avelist.append(ave)
        mincrosslist.append(minindexave)
        maxcrosslist.append(maxindexave)
    featurelist = avelist + mincrosslist + maxcrosslist
    return featurelist
        
def get_all_crosses_maxmin(image_mat, numregions, verbose):
    rowwise = get_rowwise_crosses_maxmin(image_mat,numregions,False)
    colwise = get_rowwise_crosses_maxmin(image_mat.transpose(),numregions,False)
    totalfeatures = rowwise + colwise
    return totalfeatures

def fuzzy_histogram_distance(xlist, ylist, bound):
    numgrid = 4
    w = float(bound)/float(numgrid)
    h = float(bound)/float(numgrid)
    
    grid = np.zeros([numgrid+1,numgrid+1])
    for index in range(0,len(xlist)):
        lowerx = int(math.floor(xlist[index]/w))
        lowery = int(math.floor(ylist[index]/h))
        gridx = [lowerx, lowerx+1, lowerx, lowerx+1]
        gridy = [lowery, lowery, lowery+1, lowery+1]
        for j in range(0,len(gridx)):
            grid[gridx[j]][gridy[j]] += (w - abs(gridx[j]*w - xlist[index]))/w * (h - abs(gridy[j]*h - ylist[index]))/h
    gridvector = grid.flatten().tolist()
    return gridvector
    
a = np.asmatrix([[0,1,2],[0,4,0],[0,7,8],[0,2,1],[0,1,2]])
print(a)
print(a.transpose())
print(get_all_crosses_maxmin(a,2,False))

bx = [1,4,6,7,2,3,6,7,4,2,9.99]
by = [1,2,5,6,7,7,2,3,4,6,9.99]
c = fuzzy_histogram_distance(bx, by, 10)
print(c)