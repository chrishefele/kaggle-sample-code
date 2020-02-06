
import cv2
import sys

f_in  = sys.argv[1]


img = cv2.imread(f_in)

RGB = (0,1,2)
for chan in RGB: 
    hist  = cv2.calcHist([img], [chan], None, [256], [0,256])
    ihist = hist.flatten().astype(int)
    zeros = sum(ihist == 0)
    print "zeros: %i chan: %i file: %s " % (zeros, chan, f_in) 

#imsave(f_out, im)



