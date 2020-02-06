import sys
sys.path.append('..')
from SETTINGS import *;
tag = 10;
fcn_img_size=256;
net_version = 1;
heart_delta_multiplier = 1.8; 
para_ss = 150;
do_cv = False;
num_epochs = 300;

shift = 15;
rotation = 30;
scale = 0.10;

no_contour_type = 'L';#other versions worse, so it's fixed to 'L'
