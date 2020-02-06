# mrmr_rank 
# Chris Hefele, 1/2/2012
#
# SUMMARY:
# This module uses the mRMR (minimum-redundancy maximum-relevance) 
# algorithm to rank the features/files used by qblend by importance. 
# Deleting the least-important files may help fight overitting to noise, 
# in addition to using the proper regularizatoin in qublend.
# This code reports the ranking; it does not modify the blending (at least not yet)
#
# THEORY:  To use the mRMR algorithm, you need correlations between the target/leaderboard 
# data and predictions -- but without a holdout set, we don't have that, since
# since target data is hidden. But one can convert from RMSE to the dot-product 
# of a prediction (X) with the target/leaderboard set (Y), and use that
# to determine the angle between unit vectors to the predictions &
# the (unknown) target/leaderboard set. This angle can be used as a similarity metric  
# between predictions against the target/leaderboard, or other predictions.
# This similarity measure use used by mRMR to rank the features / files. 
#
# Here's some theory / derivations / algebra:
#
# ||X|| = norm of vector X, i.e. vector length, sqrt(X1^2 + ... Xn^2) 
# . = dotproduct
# * = scalar multiplication)
# N   = Number of data points (here, 50K * 100 = 5M)
# X = vector of predictions
# Y = vector of actual values (e.g. leaderboard/testing sets, unknown)
# RMSE(X) = sqrt( (1/N) * ||X-Y||^2 )
# ||X-Y||^2 = N * RMSE(X)^2
# ||X-Y||^2 = X.X + Y.Y -2*X.Y 
# Thus:  X.Y = 1/2 * (X.X + Y.Y - ||X-Y||^2)
# Y.Y = N * RMSE(0)^2  
# RMSE(0) = RMSE of all zero predictions (here, 1430.78818)
# Substituting yields:
# X.Y = 1/2 * (X.X + N*RMSE(0)^2  - N*RMSE(X)^2 )
# X.Y = ||X|| * ||Y|| * cos(Angle(X,Y))
# cosAngle(X,Y)  = X.Y / (sqrt(X.X) * sqrt(Y.Y))
# cosAngle is the distance metric; cosine of angle between normalized versions of X & Y

# relevence  = abs(     cosAngle(Xcandidate,Y))
# reduncancy = abs(mean( [cosAngle(Xcandidate,Xp) for Xp in Xpicked] )
# mrmr_score = relevence - redundancy

import sys
import numpy
from math import sqrt
RMSE0 = 1430.78818 # RMSE of all-0 submission
NPTS  = 50*1000 * 100  # 5M predictions per file

def shortfn(filename): # return just the filename, given /path/filename
    return( filename.split("/")[-1] )

class MRMR_Rank:
    
    def dotprod(self, x1,x2): 
        return(float(numpy.sum(numpy.sum(x1*x2)))) # double sum due to nested arrays

    def __init__(self, predfile_list):
        self.precompute_distances(predfile_list)
        self.mrmr_rank_predfiles(predfile_list)

    def precompute_distances(self, predfile_list):
        print "MRMR: precomputing distances"
        # distmatrix is cos(Angle) of angular distance between 2 prediction set vectors
        self.distmatrix = {}
        for p1 in predfile_list:
            for p2 in predfile_list:
                xdoty = self.dotprod(p1.data, p2.data)
                xdotx = self.dotprod(p1.data, p1.data)
                ydoty = self.dotprod(p2.data, p2.data)
                self.distmatrix[(p1.filename, p2.filename)] = xdoty / sqrt( xdotx * ydoty )
                #print p1.filename, p2.filename, self.distmatrix[(p1.filename, p2.filename)] 
            print p1.filename
            sys.stdout.flush()
        # distvec is cos(Angle) of angular distance between a prediction set vector & target/leaderboard
        self.distvec = {}
        for p1 in predfile_list:
            xdotx = self.dotprod(p1.data, p1.data)
            xdoty = 0.5*( xdotx + NPTS*pow(RMSE0,2) - NPTS*pow(p1.rmse,2) ) 
            ydoty = NPTS * pow(RMSE0,2) 
            self.distvec[p1.filename] = xdoty / sqrt( xdotx * ydoty )
            # print p1.filename, self.distvec[p1.filename] 
            print p1.filename
            sys.stdout.flush()
        print "\nMRMR: Done precomputing distances\n"

    def mrmr_rank_predfiles(self, predfile_list):
        candidate_predfiles = [ p for p in predfile_list] # make a working copy
        selected_predfiles = []        
        print "Ranking importance of", len(candidate_predfiles),"files via mRMR\n"
        while candidate_predfiles:
            best_mrmr_score = -999999999
            best_candidate  = None
            for candidate in candidate_predfiles:  
                mrmr_score = self.mrmr_score(candidate, selected_predfiles)
                print "  mRMR score:", mrmr_score, shortfn(candidate.filename)
                if mrmr_score > best_mrmr_score:
                    best_mrmr_score = mrmr_score
                    best_candidate  = candidate                    
            print "SELECTED:",shortfn(best_candidate.filename),"with mRMR score:", best_mrmr_score,"\n"
            selected_predfiles.append( best_candidate)
            candidate_predfiles.remove(best_candidate)                                                   

        print "\nMRMR FILE RANKING (BEST TO WORST)"
        for pf in selected_predfiles:
            print pf.rmse, ",", shortfn(pf.filename)
        return(selected_predfiles)
    
    def mrmr_score(self, candidate_predfile, selected_predfiles):    
        relevence = self.distvec[candidate_predfile.filename]
        redundancy = 0.0
        if selected_predfiles: 
            for selected_predfile in selected_predfiles:
                redundancy += self.distmatrix[(selected_predfile.filename, candidate_predfile.filename)]
            redundancy = redundancy / len(selected_predfiles)           
        return relevence - redundancy
        # return relevence / redundancy                             # <<<<< try this, but watch /0? 
   
    
