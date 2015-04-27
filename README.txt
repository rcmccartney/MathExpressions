Extracting the program:
1. Unzip program.zip
2. tar -xvzf program.tgz

Running the program:
$ python3 execute.py [flag] [arguments]

Flags to use:
-p                  : perform parsing and save to file
-s <percent>        : perform splitting on <percent>% of data in (% in range [0,1]) and save to file
-e                  : perform feature extraction and save to file
-tc                 : train the classifier with the data passed in, set segment to 1.0 to use all data
-test               : perform a complete test with unseen data
  ==>With -seg flag set will test segmentation, otherwise will test only classification
-seg                : perform segmentation (will use either training or testing data)
-m [name]           : specify model to use for testing (inside models dir)
                      Available models: '1nn.pkl' - 1-nearest neighbor
                                        'rf.pkl' - random forest
                                        'bdt.pkl' - AdaBoost with decision tree weak learners
                                        'rbf_svm.pkl' - SVM with RBF kernel
-p [params]         : load parameters for testing from params dir instead of default location
-d [dir1 dir2...]   : operate on the specified directories
-f [file1 file2...] : operate on the specified files
-l [filelist.txt]   : operate on the files listed in the specified text file
-ol [outdir]        : specify the output directory for .lg files
-om [dir]           : specify the models directory
-v [int]            : turn on verbose output [1=minimal, 2=maximal]
-g [file]           : specify grammar file location


EXAMPLE USAGES:

To train the classifier model on all of some pre-parsed data (from an earlier execution with -p):
$ python3 execute.py -e -s 1.0 -tc -v 2

To train the classifier model with a 0.7/0.3 split of data (on files listed in <fileList>):
$ python3 execute.py -p -e -s 0.7 -tc -v 1 -l <fileList>

Then to run segmentation with this trained classifier on pre-segmented data:
$ python3 execute.py -seg

To run a trained model on unseen data for testing segmentation results from a directory*:
$ python3 execute.py -test -p -seg -d <dir>

*Note the pipeline can also be broken into separate steps 
of parsing then segmentation with two separate execution calls.
A trained classifier and trained feature extractor are required 
to perform testing or you will receive an assertion error.

