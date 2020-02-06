#!/usr/bin/python2
import heart;
import SETTINGS as c;
import sys
import os

if __name__=='__main__':
    """
    extract the sex and age information for each case,
    it will be used to build the age-sex model
    """
    import sys;
    import time;
    M = int(sys.argv[1]);
    N = int(sys.argv[2]);
    if M == 1:
        info = open(c.output_dir +"/info.csv","w");
        info.write("Id,age,sex\n");
    else:
        info = open(c.output_dir+"/info.csv","a");

    for case in range(M,N+1):
        direcs = [os.path.join(c.data_kaggle, 'train'),
                os.path.join(c.data_kaggle, 'validate'),
                os.path.join(c.data_kaggle,'test')]
        s = str(case);
        direc = next(p for p in direcs if os.path.exists(os.path.join(p, s)))
        dset = heart.Dataset(os.path.join(direc,s),s);
        v = dset.info;
        info.write("%d,%.3f,%s\n"%(case,v[0],v[1]));

    info.close();
