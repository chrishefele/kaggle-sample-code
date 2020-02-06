# shiftMetrics.py  
#
# Adds position-shifted versions of each metric to existing metrics
#
# usage: python shiftMetrics.py <metrics_infile>  <metrics_outfile> 
#

import pandas
import numpy
import sys

SHIFTS = [-1,1]  # lagging & leading one position

def getFileData(fname):
    print "reading:", fname
    return pandas.read_csv(fname)

def writeFileData(df, fname):
    print "writing:", fname
    df.to_csv(fname, index=False)

def shiftMetrics(df, shifts):
    print "input data shape:", df.shape
    col_names = tuple(df.columns)

    for shift in shifts:
        if shift > 0:
            prefix = 'LEAD_%02i_' % shift
        elif shift < 0 :
            prefix = 'LAG_%02i_' % abs(shift)
        else:
            continue
        print "using shift value:", shift
        for col in col_names:
            if col not in ['Truth','Index']:
                df[prefix+col] = numpy.array(numpy.roll(df[col], shift))
                print "  adding:", prefix+col

    print "data shape with added shift metrics:", df.shape
    return df

def main():
    print '*** Shift Metrics ***'
    infile  = sys.argv[1]
    outfile = sys.argv[2]

    metrics = getFileData(infile)
    metrics = shiftMetrics(metrics, SHIFTS)
    writeFileData(metrics, outfile)

if __name__ == '__main__':
    main()

