import os
import sys
sys.path.append('..')
import SETTINGS as sts

data_root = sts.data_root
data_kaggle = sts.data_kaggle
data_sunnybrook = sts.data_sunnybrook
data_manual = sts.data_manual
data_intermediate = sts.data_intermediate

params_dir = sts.local_root + 'tencia_scripts/params'
output_dir = sts.local_root + 'tencia_scripts/output'

fcn_img_size=246
fcn_train_epochs=300
ch4_train_epochs=150

fcn_eval_cases = (1,1141)
ch4_eval_cases = (1,1141)

include_validation_images = True

'''
fcn_train_epochs=3
ch4_train_epochs=3
fcn_eval_cases = (1,10)
ch4_eval_cases = (1,10)
'''
