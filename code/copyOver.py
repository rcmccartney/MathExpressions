#!/usr/local/bin/python3

import sys
import os
import shutil
from os import walk

indir =  sys.argv[1]
cpdir = sys.argv[2]

print("in", indir, "from", cpdir)
input("enter")

f = []
for (dirpath, dirnames, filenames) in walk(sys.argv[2]):
	f.extend(filenames)
	break

os.makedirs("temp_test")

g = []
for (dirpath, dirnames, filenames) in walk(sys.argv[1]):
	g.extend(filenames)
	break

# only keep in g what is in f
for filen in g:
	if filen in f:
		print("copying", filen)
		shutil.copyfile(filen, os.path.join("temp_test", filen))
	else:
		print("skipping", filen)
