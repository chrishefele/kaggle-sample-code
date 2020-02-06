
import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
 
a = np.array([0,0], dtype='float32')
def getXY(imgPath):
 
    try:
        os.environ["DEBUG"]
        DEBUG = 1
     
        print "-------------------------------"
        print "Using OpenCV version : ",cv2.__version__
        print "-------------------------------"
        print "TASK : Mimic getxy() feature of MATLAB"
        print "***************************************"
         
    except KeyError:
        #print "For verbose mode, set DEBUG flag"
        DEBUG = 0
     
    #define the event
    def getxy(event, x, y, flags, param):
       global a
       if event == cv2.EVENT_LBUTTONDOWN :
          a = np.vstack([a, np.hstack([x,y])])
          if (DEBUG):
            print "(row, col) = ", (x,y)
     
       #Read the image
       img = cv2.imread(imgPath)
       if (DEBUG):
          print "Reading the image..."
     
       #Set mouse CallBack event
       cv2.namedWindow('image')
       cv2.setMouseCallback('image', getxy)
       if (DEBUG):
          print "Set MouseCallback functionality..."
     
       #show the image
       print "Click to select a point OR press ANY KEY to continue..."
       cv2.imshow('image', img)
       cv2.waitKey(0)
       cv2.destroyAllWindows()
     
       #obtain the matrix of the selected points
       b = a[1:,:]
       if (DEBUG):
          print ""
          print "The clicked points..."
          print b, b.dtype, b.shape
     
       print "The selected points are returned as a float64 MATRIX..."
       return b
