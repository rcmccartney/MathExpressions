from code.features import *
from code.classifier import *
from execute import *


class Segmenter():

        def __init__(self):

            self.best_list = []
            self.backtrack_list = []
            self.bestclass_list = []
            self.trace_ids = []
            self.test_data = None

        def segment_inkml_files(self, test_data, feature_extractor, classifier):

            self.test_data = test_data
            best_list = []
            backtrack_list = []
            bestclass_list = []
            trace_ids_list = []
            for inkmlfile in test_data:
                trace_list = inkmlfile.get_trace_list()
                best = []
                backtrack = []
                bestclass = []
                # input to eval is a list of traces - need to get feature set for this
                temp_symbol = Symbol(None, None, None, None, [trace_list[0]])
                feature_set = feature_extractor.get_single_feature_set(temp_symbol,0)
                maxkey, maxdist = classifier.eval(feature_set, 1)
                print("maxkey", maxkey)
                print("maxdist", maxdist)
                best.append(maxdist)  # index 0
                backtrack.append(-1)  # indicates start of array
                bestclass.append(maxkey)
                for i in range(1, len(trace_list)):
                    print("-----")
                    best.append(float("-inf"))
                    backtrack.append(-1)
                    bestclass.append("temp")
                    for j in range(i-1, -1, -1):
                        subset = trace_list[j+1:i+1]
                        print("subset: ", j+1, ", ", i+1)
                        temp_symbol = Symbol(None, None, None, None, subset)
                        feature_set = feature_extractor.get_single_feature_set(temp_symbol,0)
                        maxkey, maxdist = classifier.eval(feature_set, len(subset))
                        print("maxkey: ", maxkey, "maxdist: ", maxdist)
                        dist = best[j] + maxdist
                        if dist > best[i]:
                            best[i] = dist
                            backtrack[i] = j
                            bestclass[i] = maxkey
                    #special case: all traces up to and including i are one character
                    temp_symbol = Symbol(None, None, None, None, trace_list[0:i+1])
                    feature_set = feature_extractor.get_single_feature_set(temp_symbol,0)
                    maxkey, maxdist = classifier.eval(feature_set, (i+1))
                    if maxdist > best[i]:
                        best[i] = maxdist
                        backtrack[i] = -1
                        bestclass[i] = maxkey
                print(best)
                print(backtrack)
                print(bestclass)
                print("")
                print("")
                print("")
                best_list.append(best)
                backtrack_list.append(backtrack)
                bestclass_list.append(bestclass)
                
                #get the trace id's
                trace_ids = []
                for trace in trace_list:
                    trace_ids.append(trace.id)
                trace_ids_list.append(trace_ids)
                    
            self.best_list = best_list
            self.backtrack_list = backtrack_list
            self.bestclass_list = bestclass_list
            self.trace_ids = trace_ids_list

        def backtrack(self):
            pass

