import numpy
import scipy.misc
import pylab
import scipy.ndimage
import sys

def writeImageFFT(image_infile, fft_outfile):
    image = pylab.imread(image_infile)
    image = pylab.mean(image,2)
    # image = scipy.ndimage.gaussian_filter(image, sigma=1) # TODO smoothing - remove? 
    fft_image = pylab.fftshift(pylab.fft2(image))
    psd2d = numpy.log10(pow( numpy.abs(fft_image), 2))
    scipy.misc.imsave(fft_outfile, psd2d)

def imageFFTs(imagefile):
    image = pylab.imread(imagefile)
    image = pylab.mean(image,2)

    fft_image = pylab.fftshift(pylab.fft2(image))
    psd2d = pow( numpy.abs(fft_image), 2)

    blurred = scipy.ndimage.gaussian_filter(image, sigma=2)
    fft_blurred = pylab.fftshift(pylab.fft2(blurred))
    psd2d_blurred = pow( numpy.abs(fft_blurred), 2)

    pylab.gray()
    pylab.subplot(2,2,1)
    pylab.title('Original image')
    pylab.imshow(image)

    pylab.subplot(2,2,2)
    pylab.title('psd2d')
    pylab.imshow(image)
    pylab.imshow(numpy.log10(psd2d))

    pylab.subplot(2,2,3)
    pylab.title('blurred')
    pylab.imshow(blurred)

    pylab.subplot(2,2,4)
    pylab.title('psd2d_blurred')
    pylab.imshow(numpy.log10(psd2d_blurred))
    pylab.show()


def old_main():
    IMAGE_FILES = ['../data/tmp/train10000.png', '../data/tmp/train10001.png']
    for image_file in IMAGE_FILES:
        imageFFTs(image_file)

def main():
    infile  = sys.argv[1]
    outfile = sys.argv[2]
    writeImageFFT(infile, outfile)

main()


