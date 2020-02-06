import numpy

MAXBITS = 16

on_bits_count = numpy.zeros(MAXBITS+1,dtype=int)
for n in xrange(pow(2,MAXBITS)-1):
    on_bits = bin(n).count('1')
    on_bits_count[on_bits] += 1
print on_bits_count
print sum(on_bits_count)
binary_counts = on_bits_count

on_bits_count = numpy.zeros(MAXBITS+1, dtype=int)
for n in xrange(pow(2,MAXBITS)-1):
    thresh = numpy.random.random()
    on_bits  = sum(numpy.random.random(MAXBITS) > thresh)
    on_bits_count[on_bits] += 1
print on_bits_count
print sum(on_bits_count)
uniform_density_counts = on_bits_count

print
print 1. * binary_counts / uniform_density_counts



