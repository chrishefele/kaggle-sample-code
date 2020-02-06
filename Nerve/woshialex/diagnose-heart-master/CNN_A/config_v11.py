import sys
sys.path.append('..')
from SETTINGS import *;
tag = 11;
fcn_img_size=196;
net_version = 2;
heart_delta_multiplier = 1.8; 
para_ss = 150;
do_cv = False;
num_epochs = 250;

shift = 10;
rotation = 15;
scale = 0.15;

no_contour_type = 'L';#other versions worse, so it's fixed to 'L'
