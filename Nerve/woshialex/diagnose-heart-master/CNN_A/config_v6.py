import sys
sys.path.append('..')
from SETTINGS import *;
tag = 6;
fcn_img_size=196;
net_version = 2;
heart_delta_multiplier = 1.6; 
para_ss = 100;
do_cv = False;
num_epochs = 250;

shift = 10;
rotation = 20;
scale = 0.15;

no_contour_type = 'L';#other versions worse, so it's fixed to 'L'
