import numpy as np
import matplotlib.pyplot as plt
import pickle

x = np.arange(0, 5, 0.1);
y = np.sin(x)
xTemp = pickle.load(open("xTemp.p","rb"))
yTemp = pickle.load(open("yTemp.p","rb"))
for i in range(0,3):
    plt.figure()
    plt.plot(xTemp, yTemp)
plt.show()