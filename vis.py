import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import numpy
import sys

x = np.loadtxt(sys.argv[1])
plt.imshow(x, cmap = cm.Greys_r)
plt.savefig("test.png", interpolation='nearest')