# xfeatures_sync.py
#
# Usage:  python xfeatures_sync.py   feature_file1.csv  feature_file2.csv ...
#
# This program rewrites HHP feature files so they all have a common set of 
# columns/features. Unique columns may appear in a file if one value of a 
# variable appears in only one dataset (e.g. a 26+ week length-of-stay 
# is only in Y3). Any columns/features unique to one file are deleted.
# Files are rewritten with a new prefix/suffix (see constants below), and
# contain only the columns/features all files have in common. 
#

import pandas 
import sys

REWRITE  = True     # flag to turn on/off rewriting
F_SUFFIX = ''       # file suffix for rewritten file, or '' for overwriting

def colnames(fname): 
    return set(pandas.read_csv(fname, nrows=1).columns.tolist())

print "\n*** Sync Feature File Columns ***\n"
fnames = sys.argv[1:]
f_colnames = {}
for fname in fnames:
    f_colnames[fname] = colnames(fname)
    print "Read:", fname, "\t#Columns:", len(f_colnames[fname])

common_names = reduce(set.intersection, f_colnames.values())
print "\nCommon column names across files:"
for n, common_name in enumerate(sorted(common_names)):
    print "  ",n, common_name
print

for fname in fnames:
    uniq_names = f_colnames[fname] - common_names
    print "Found unique names in file:", fname
    for uniq_name in sorted(uniq_names):
        print "  ", uniq_name 

    if REWRITE:
        fout = fname + F_SUFFIX
        print "Preparing to rewrite:", fname,"as:", fout
        print "Reading:", fname
        sys.stdout.flush()
        df = pandas.read_csv(fname)
        for uniq_name in uniq_names:
            del df[uniq_name]
        df.set_index('MemberID', inplace=True)
        df = df.sort_index(axis=1)
        print "Writing:", fout
        sys.stdout.flush()
        df.to_csv(fout)
    print 

print "Done."

