import pandas
import time
import numpy

df = pandas.DataFrame({'a':range(1,100), 'b':range(101,200)})

LOOPS = 100000

t0=time.time()
for _ in xrange(LOOPS):
    v = df['a'][3]
print time.time()-t0


t0=time.time()
for _ in xrange(LOOPS):
    v = df.a[3]
print time.time()-t0


t0=time.time()
for _ in xrange(LOOPS):
    v = df.get_value(3,'a')
print time.time()-t0


ax = numpy.array(df['a'])
t0=time.time()
for _ in xrange(LOOPS):
    v = ax[3]
print time.time()-t0



