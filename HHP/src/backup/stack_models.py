# stack_models.py 
#
# by CJH 12/2012
#
# Purpose: Take individual predictions/submission files for different 
# individual HHP models and merge them together to create a features 
# file for stacking / blending. Essentially, it pastes columns
# & does some additional checks for consistency. 
#
# Note: this assumes the filename format for the model/prediction
# files has the following format:  Ytrain-Ytest-xx-xx-xx.csv 
# where Ytrain and Ytest are the year to train/test on, respectively.
# e.g. Y1, Y2, or Y1Y2.  The remaining pieces (xx-xx-xx) are options
# used for the model; these are used for column labels.
#

import pandas 
import sys
import os

MODELS_DIR = '/home/chefele/kaggle/HHP/models/predictions/'  
STACK_DIR  = '/home/chefele/kaggle/HHP/stack/features/'

print "\n*** Stack Models ***\n"
print "Reading models   directory: ", MODELS_DIR
print "Writing features directory: ", STACK_DIR
print

all_models = {}     # all models, partitioned by Ytrain-Ytest combination
all_model_options = set()
nfiles = 0 

for fname in sorted(os.listdir(MODELS_DIR)):

    prefix, extension = fname.split('.')
    tokens            = prefix.split('-')
    model_options     = '-'.join(tokens[2:])
    yr_train, yr_test = tokens[0], tokens[1]
    model_yrs         = '-'.join([yr_train, yr_test])

    print "  ", fname
    df = pandas.read_csv(MODELS_DIR + fname)
    df.set_index('MemberID', inplace=True)
    df.columns = [model_options] # rename col to the set of options
    all_model_options = all_model_options.union(set([model_options]))

    if model_yrs not in all_models:
        all_models[model_yrs] = pandas.DataFrame()
    all_models[model_yrs] = all_models[model_yrs].merge(df, how='outer', \
                                        left_index=True, right_index=True)
    sys.stdout.flush()
    nfiles += 1

print "\nRead:",nfiles,"files from", MODELS_DIR,"\n"

for model_yrs in sorted(all_models):
    fout = STACK_DIR + model_yrs + '.csv'
    print "Writing  ", fout, " with the following data:"
    df = all_models[model_yrs] 
    df = df.sort_index(axis=1) # sort columns by options name(s)
    print
    print df
    print
    missing_cols = all_model_options - set(df.columns)
    if missing_cols:
        print "\n*** WARNING: These columns missing in:",fout
        for missing_col in missing_cols:
            print '  ', missing_col
        print
    sys.stdout.flush()
    df.to_csv(fout)  # finally...save it!

print "Done.\n"


