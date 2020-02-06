#!/bin/bash -v

python build_analog.py
./build_train+test+unlabeled_data.sh
python build_binary.py

./build_bsvd_datafiles.sh


