#!/usr/local/bin/python3

import os
import sys
from os import walk

if not os.path.exists("out"):
	os.makedirs("out")

f = []
for (dirpath, dirnames, filenames) in walk("."):
	f.extend(filenames)
	break
f.remove("script.py")

for filen in f:
	if filen[0:4] == "frdb":
		newfilen = "M" + filen
	else:
		newfilen = filen
	print(filen)
	with open(filen, "r") as fin:
		with open(os.path.join("out", newfilen), "w") as fout:
			for line in fin:
				line = line.strip().split()
				for i in range(len(line)):
					if line[i] == ",,":
						line[i] = "COMMA,"
					if line[i][0:2] == ",_":
						line[i] = "COMMA" + line[i][1:]
					if i == len(line) - 1:
						fout.write(line[i] + "\n")
					else:
						fout.write(line[i] + " ")
