import aifc, os
path = '../download/train2/'
for fname in os.listdir(path):
    fin = aifc.open(path+fname, 'r')
    print fin.getparams(),
    markers = fin.getmarkers()
    print markers

