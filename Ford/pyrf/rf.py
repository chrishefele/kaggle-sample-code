import milk 
import time
from milk.supervised import randomforest
import numpy 

TRAIN_FILE = "/home/chefele/Ford/download/fordTrain.csv"

print "Reading from:",TRAIN_FILE
features = numpy.loadtxt( TRAIN_FILE, delimiter=",", skiprows=1, usecols=tuple(range(4,10)) )  # <<<<** 6 features
print "Done reading features"

# TrialID,ObsNum,IsAlert,P1,P2,P3,P4,P5,P6,P7,P8,E1,E2,E3,E4,E5,E6,E7,E8,E9,E10,E11,V1,V2,V3,V4,V5,V6,V7,V8,V9,V10,V11
labels = numpy.loadtxt( TRAIN_FILE, delimiter=",", skiprows=1, usecols=(3,) ) 
print "Done reading labels"

# subset for faster training 
print "Creating subset"
features = features[1:80000]
labels   = labels[  1:80000]

print "Features shape:", features.shape
print "Labels shape:", labels.shape
print "Starting tree learning..."
T0=time.time()
treelearner = milk.supervised.tree.tree_learner()
model = treelearner.train(features,labels)
print "Tree learning time:", time.time()-T0,"seconds"


# rflearner = randomforest.rf_learner(rf=1,frac=frac_now)     # **** try just 1 tree for timing purposes 
# model = rflearner.train(features, labels)

new_labels = model.apply(features[1])
print new_labels

# cmat, names, preds = milk.nfoldcrossvalidation(features, labels, classifier=learner, return_predictions=1)

