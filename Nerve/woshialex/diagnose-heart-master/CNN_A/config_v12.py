import sys
sys.path.append('..')
from SETTINGS import *;
tag = 12;
fcn_img_size=256;
net_version = 1;
heart_delta_multiplier = 1.5; 
para_ss = 75;
do_cv = False;
num_epochs = 300;

shift = 5;
rotation = 15;
scale = 0.1;

no_contour_type = 'L';#other versions worse, so it's fixed to 'L'
