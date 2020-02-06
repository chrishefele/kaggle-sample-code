import sys
import pandas
import collections
from collections import namedtuple
from datetime import datetime

CSV_FILE = '../download/train.csv'
# CSV_FILE   = '../download/train-001000.csv'

def daysElapsed(datetimeStr, datetimeOrigin="01JAN00:00:00:00"):
    if not datetimeStr:
        return -1
    fmt = "%d%b%y:%H:%M:%S"
    elapsed =   datetime.strptime(datetimeStr,    fmt) - \
                datetime.strptime(datetimeOrigin, fmt)
    return elapsed.days

def is_date(s):
    try:
        daysElapsed(s)
    except ValueError:
        return False
    else:
        return True

def all_nines(i):
    assert isinstance(i, int)
    uniq_digits = set(str(abs(i))) 
    return True if i >= 99 and uniq_digits == set('9') else False

def ninesSentinels(sentinelValue):
    assert all_nines(sentinelValue)
    if sentinelValue > 0:
        return range(sentinelValue-9, sentinelValue+1)
    else:
        pass
        # TODO return range(sentinelValue-9, sentinelValue+1)
        


IntSeries    = namedtuple('IntSeries',    ['sentinel_lo', 'sentinel_hi'])
FloatSeries  = namedtuple('FloatSeries',  ['sentinel_lo', 'sentinel_hi'])
NullSeries   = namedtuple('NullSeries',   [])
StringSeries = namedtuple('StringSeries', [])
DateSeries   = namedtuple('DateSeries',   [])
BoolSeries   = namedtuple('BoolSeries',   [])

def col_type(col):
    # type counts: (1594 int64), (290 float64), (37 object), (13 bool)
    if len(col) == 0:
        return NullSeries()

    cmin = min(col.values)
    cmax = max(col.values)
    vals_lo = tuple(sorted(col.unique()))[  :5]
    vals_hi = tuple(sorted(col.unique()))[-5:]

    if   col.dtype.name == 'int64':
        return IntSeries( sentinel_lo = (cmin == -1) or all_nines(cmin), \
                          sentinel_hi = all_nines(cmax) )

    elif col.dtype.name == 'float64':
        return FloatSeries(
                         sentinel_lo = (cmin == -1.0) or all_nines(int(cmin)), 
                         sentinel_hi = all_nines(int(cmax)) ) 

    elif col.dtype.name == 'object':
        if is_date(cmin) or is_date(cmax):
            return DateSeries() 
        else:
            return StringSeries() 

    elif col.dtype.name == 'bool':
        BoolSeries()
    else:
        raise TypeError, "Unknown type"


def colorSentinelList(lst):
    START_RED = '\033[91m'
    UNDERLINE = '\033[4m'
    END_COLOR = '\033[0m'

    colored_items = []
    for item in lst:
        if item in (-1, -1.0) or not isinstance(item, str) and all_nines(int(item)):
            colored_items.append(START_RED + str(item) + END_COLOR)
        else:
            colored_items.append(str(item))
    return '[' + ', '.join(colored_items) + ']'





def classify_column_types(csv_file):
    df = pandas.read_csv(csv_file)
    for col_name in df:
        # print col_name, col_type(df[col_name])
        col = df[col_name]

        #isnull  = sum(col.isnull())
        #notnull = sum(col.notnull() )
        uniq    = len(col.unique() )
        #nvals   = len(col.values   ) 

        col     = col[col.notnull()]  # TODO think about how to handle nulls; replace? new flag? 
        coltype = col_type(col)

        print col_name, coltype, ("uniq: %06i" % uniq)
        v = list(sorted(col.unique()))
        print 'First values:', colorSentinelList(v[   :10])
        print 'Last  values:', colorSentinelList(v[-10: ])
        print 


def main():
    classify_column_types(CSV_FILE)

if __name__ == '__main__':
    main()

