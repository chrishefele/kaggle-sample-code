import sys
sys.path.append('..')
from SETTINGS import *;
tag = 13;
fcn_img_size=196;
net_version = 2;
heart_delta_multiplier = 1.8; 
para_ss = 75;
do_cv = False;
num_epochs = 300;

shift = 15;
rotation = 25;
scale = 0.2;

no_contour_type = 'L';#other versions worse, so it's fixed to 'L'
