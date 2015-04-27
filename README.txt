Running the program:
    
$ python3 parseAndExecute.py [flag] [arguments]

Flags to use:
-t <model_dir>      : train classifier (no flag set will perform testing)
-m [name]           : specify model to use for testing (inside params dir)
                      Available models: '1nn.pkl' - 1-nearest neighbor
                                        'rf.pkl' - random forest
                                        'bdt.pkl' - AdaBoost with decision tree weak learners
                                        'rbf_svm.pkl' - SVM with RBF kernel
-p [params]         : load parameters for testing from params dir instead of default location
-d [dir1 dir2...]   : operate on the specified directories
-f [file1 file2...] : operate on the specified files
-l [filelist.txt]   : operate on the files listed in the specified text file
-o [outdir]         : specify the output directory for .lg files
-v [int]            : turn on verbose output [1=minimal, 2=maximal]
-g [file]           : specify grammar file location
-skip               : flag to skip the parsing step and load from parsed.pkl

To run the model on unseen data:

Ex: Run the SVM on unseen data using inkml files stored in <FILE> with verbose output:

$ python3 parseAndExecute.py -m rbf_svm.pkl -l <FILE> -v 1



HOW IT WAS TRAINED
-p -e -s 0.7 -tc -v 1 -l C:\Users\mccar_000\Dropbox\McCartney\GradSchool\Classes\Semester4\PatternRec\Project\TrainINKML_v3\AllEM_part4_TRAIN_all.txt

-seg -v 1

