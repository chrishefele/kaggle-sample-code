import sys
sys.path.append('..')
from SETTINGS import *;
tag = 5;
fcn_img_size=256;
net_version = 1;
heart_delta_multiplier = 1.6; 
para_ss = 200;
do_cv = False;
num_epochs = 300;

shift = 10;
rotation = 20;
scale = 0.15;

no_contour_type = 'L';#other versions worse, so it's fixed to 'L'
