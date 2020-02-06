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

"""  Commented out Semi-supervised code below (which runs slowly), 
     in order to make testing Gaussian Naive Bayes easier.

# Semi-supervised Bayes
print "Semi-supervised naive bayes..."
clf = naive_bayes.MultinomialNaiveBayes()
clf.fit_semi(tdTrain, c, tdUnlabeled)
pred = clf.predict(tdTest)
"""

# Gaussian Naive Bayes  (added by CH 2/10/2012)
print "Gaussian naive bayes..."

# c has 4 cols with 0 or 1 in each, representing ratings 1-4
# so must convert to a vector containing values 1-4 for GNB
c_rows, c_cols = c.shape
c_vec = c * np.array( [[1,2,3,4]]*c_rows )  
c_vec = sum(c_vec.transpose()).transpose()

clf3 = naive_bayes.GNB()
#clf3.fit(tdTrain, c)
clf3.fit(tdTrain, c_vec)
pred3 = clf3.predict(tdTest)

"""  The following doesn't work -- it has no fit method & doesn't inherit one;
     Maybe BaseNaiveBayes() is not supposed to be callable directly? 
     Just inherit from it?  Other methods inheriting from this _DO_  define 'fit'

# Base Naive Bayes
print "Base naive bayes..."
clf4 = naive_bayes.BaseNaiveBayes()
clf4.fit_semi(tdTrain, c, tdUnlabeled)
pred4 = clf4.predict(tdTest)
"""


"""
print "Writing to .mat file..."
# Save predictions in a mat file
sio.savemat('predictions.mat',{'preds':pred,'preds2':pred2})
"""

print "Done"
