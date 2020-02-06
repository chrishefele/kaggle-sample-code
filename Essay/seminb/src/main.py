import scipy.io as sio
import numpy as np
import base
import naive_bayes

# Load matrices from matlab
print "Loading data from .mat file..."
vars = sio.loadmat('pythonVars.mat')
tdTrain = vars['tdTrain']
tdTest = vars['tdTest']
tdUnlabeled = vars['tdUnlabeled']
c = vars['c']
cflat = vars['cflat']


# Regular Bayes
print "Regular naive bayes..."
clf2 = naive_bayes.MultinomialNaiveBayes()
clf2.fit(tdTrain, c)
pred2 = clf2.predict(tdTest)

# Semi-supervised Bayes
print "Semi-supervised naive bayes..."
clf = naive_bayes.MultinomialNaiveBayes()
clf.fit_semi(tdTrain, c, tdUnlabeled)
pred = clf.predict(tdTest)

print "Writing to .mat file..."
# Save predictions in a mat file
sio.savemat('predictions.mat',{'preds':pred,'preds2':pred2})

print "Done"
