import pandas
import numpy

df = pandas.read_csv('pick_cols.txt')

col1 = numpy.array(df['tour1'])
col2 = numpy.array(df['tour2'])

bits=15
min_diff = 999999999
for n in range(pow(2,bits)):
    m = numpy.array([int(c) for c in '{:015b}'.format(n)])
    sum1 = sum(   m *col1 + (1-m)*col2 ) 
    sum2 = sum( (1-m)*col1 +    m *col2) 
    diff = abs(sum1-sum2)
    print n, sum1, sum2, diff, m
    if diff < min_diff:
        min_diff = diff
        min_diff_n = n
        min_diff_bits = m 

print min_diff_n, min_diff, min_diff_bits








