# reformatSubmission.py  <input submission>  <output submission> 
# 
# Converts a submission file from the first Whale Challenge 
# submission format to the Whale Challenge Redux submission format
# 

import sys
import pandas
import numpy 

SAMPLE_SUBMISSION = '../download/sampleSubmission2.csv'

def reformatSubmission(infile=None ,outfile=None):
    submission  = pandas.read_csv(SAMPLE_SUBMISSION)
    predictions = numpy.loadtxt(infile, delimiter=',')
    submission['probability'] = predictions
    submission.to_csv(outfile, index=False)

if __name__=='__main__':
    infile  = sys.argv[1]
    outfile = sys.argv[2]
    print "Reformatting submission:", infile," --> ",outfile
    reformatSubmission(infile=infile, outfile=outfile)

