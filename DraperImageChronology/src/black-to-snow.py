
from scipy.misc import imread, imsave
import sys
import numpy

BLACK = 0

f_in  = sys.argv[1]
f_out = sys.argv[2]

im = imread(f_in, flatten=True)
noise = numpy.random.randint(1,255+1, size=im.shape)

mask = (im == BLACK )
im[mask] = noise[mask]

imsave(f_out, im)


