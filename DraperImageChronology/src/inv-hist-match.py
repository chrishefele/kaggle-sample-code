
# invert histogram matching on an image

import cv2
import sys
import numpy

MAX = 255
MIN = 0



f_in  = sys.argv[1]
f_out = sys.argv[2]

img_in  = cv2.imread(f_in)
img_out = numpy.zeros_like(img_in)

RGB = (0,1,2)
for chan in RGB: 
    mean = img_in[:,:,chan].mean()
    hist = cv2.calcHist([img_in], [chan], None, [256], [0,256])
    hist = hist.flatten().astype(int)

    lut = numpy.zeros_like(hist)

    ptr = int(mean)
    for i in range(int(mean), MAX+1, 1):
        if hist[i] > 0:
            lut[i] = ptr
            ptr += 1

    ptr = int(mean)-1
    for i in range(int(mean)-1, MIN, -1):
        if hist[i] > 0:
            lut[i] = ptr
            ptr -= 1

    img_out[:,:,chan] = lut[ img_in[:,:,chan] ] 

    print "channel:", chan, "mean:", mean
    print "hist:", hist
    print "lut:", lut
    print

cv2.imwrite(f_out, img_out)


