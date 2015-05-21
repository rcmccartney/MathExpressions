Running the program:
$ python3 execute.py [flag] [arguments]

Flags to use:
-c                  : perform conversion of inkml files into objects for follow-on manipulation
-s <percent>        : perform splitting on <percent>% of data in (% in range [0,1]) and save to file
-e                  : perform feature extraction and save to file
-tc                 : train the classifier with the data passed in, set segment to 1.0 to use all data
-test               : perform a complete test with unseen data
  ==>With -seg flag set will test segmentation, otherwise will test only classification
-seg                : perform segmentation (will use either training or testing data)
-p                  : perform parsing of the ground-truth classification and segmentation into symbol trees
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
-g [file]           : specify grammar file location


EXAMPLE USAGES:

To train the classifier model on all of some pre-converted data (from an earlier execution with -c):
$ python3 execute.py -e -s 1.0 -tc

To train the classifier model with a 0.7/0.3 split of data (on files listed in <fileList>):
$ python3 execute.py -c -e -s 0.7 -tc -l <fileList>

To train the classifier model and segment using <dir>:
$ python3 execute.py -c -e -s 0.7 -tc -seg -d <dir>

Then to run segmentation with this trained classifier on pre-segmented data:
$ python3 execute.py -seg

To run a trained model on unseen data for testing segmentation results from a directory*:
$ python3 execute.py -test -c -seg -d <dir>

To run the trained model for parsing a tree with ground truth classification and segmentation:
$ python3 execute.py -c -p -d <dir>

*Note the pipeline can also be broken into separate steps 
of parsing then segmentation with two separate execution calls.
A trained classifier and trained feature extractor are required 
to perform testing or you will receive an assertion error.

OUTPUT:

All pickled data will appear in the outdir specified above on the command line, or 
defaulted to .\output.  Inside output, the .lg results for classification (segmentation given)
will appear in a 'classifier' subfolder, while results for segmentation will appear in a 
'segment' subfolder.  Inside each subfolder the results are broken down into directories
by training and test set, as well as by classification model used.