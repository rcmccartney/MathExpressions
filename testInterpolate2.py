import numpy
import pylab
import math

def resample_points(xList, yList, alpha):
    acc_len = []
    acc_len.append(0.0)
    for i in range(1,len(xList)):
        Li = acc_len[-1] + math.sqrt( math.pow((xList[i]-xList[i-1]),2) + math.pow((yList[i]-yList[i-1]),2))
        acc_len.append(Li)
    m = math.floor(acc_len[-1]/alpha)
    xListNew = []
    yListNew = []
    xListNew.append(xList[0])
    yListNew.append(yList[0])
    j = 1
    for p in range(1,(m-2)):
        while acc_len[j] < p*alpha:
            j += 1
        c = (p*alpha - acc_len[j-1])/(acc_len[j] - acc_len[j-1])
        xNew = xList[j-1] + (xList[j]-xList[j-1])*c
        yNew = yList[j-1] + (yList[j]-yList[j-1])*c
        xListNew.append(xNew)
        yListNew.append(yNew)
    xListNew.append(xList[-1])
    yListNew.append(yList[-1])
    return xListNew, yListNew
    
xxx = [1, 3, 4, 1, 2, 9]
yyy = [2, 7, 4, 3, 1, 3]
pylab.plot(xxx,yyy,'o')
xn, yn = resample_points(xxx,yyy,0.01)
pylab.plot(xn,yn,'x')
pylab.show()