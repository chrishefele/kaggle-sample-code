""" genTrainMetrics.py

    This file generates the training metrics
"""
import globalConst
from printStatus import printStatus

import numpy as np
import pylab as pl

import metrics
import plotting
import fileio
import templateManager
import cv2

def fileID(filename): 
    """ parse file ID from train filename, e.g. trainNNNN.aiff -> NNNN"""
    return int(filename.split('.')[0][5:]) - 1

def main():

    baseDir     = globalConst.BASE_DIR

    ###################### SET OUTPUT FILE NAME HERE ########################
    trainOutFile = baseDir+'workspace/trainMetrics.csv'
    
    ############################## PARAMETERS ###############################
    dataDir         = baseDir+'data/'              # Data directory
    templateDataDir = baseDir+'template_data/'     # Data directory

    params = {'NFFT':256, 'Fs':2000, 'noverlap':192} # Spectogram parameters
    maxTime = 60 # Number of time slice metrics

    ######################## BUILD A TrainData OBJECT #######################
    train         = fileio.TrainData(        dataDir+'train.csv',dataDir+'train/')
    templateTrain = fileio.TrainData(templateDataDir+'train.csv',templateDataDir+'train/')

    ##################### BUILD A TemplateManager OBJECT ####################
    tmplFile = baseDir+'moby/templateReduced.csv'
    tmpl = templateManager.TemplateManager(fileName=tmplFile, 
                                           trainObj=templateTrain, params=params)

    ################## VERTICAL BARS FOR HIFREQ METRICS #####################
    bar_ = np.zeros((12,9),dtype='Float32')
    bar1_ = np.zeros((12,12),dtype='Float32')
    bar2_ = np.zeros((12,6),dtype='Float32')
    bar_[:,3:6] = 1.
    bar1_[:,4:8] = 1.
    bar2_[:,2:4] = 1.

    ########################### CREATE THE HEADER ###########################
    outHdr = metrics.buildHeader(tmpl)

    ###################### LOOP THROUGH THE FILES ###########################
    hL = []
    print "\nprocessing whale clips"
    for i in range(train.numH1):
        printStatus(i)
        clip_filename = train.h1[i]
        fid = fileID(clip_filename) 

        P, freqs, bins = train.H1Sample(i,params=params)
        out  = metrics.computeMetrics(P, tmpl, bins, maxTime)
        out += metrics.highFreqTemplate(P, bar_)
        out += metrics.highFreqTemplate(P, bar1_)
        out += metrics.highFreqTemplate(P, bar2_)
        #hL.append([1, i] + out)
        hL.append( (fid, [1,i]+out) ) # NOTE added fid for sorting below

    print "\nprocessing non-whale clips"
    for i in range(train.numH0):
        printStatus(i)
        clip_filename = train.h0[i]
        fid = fileID(clip_filename) 

        P, freqs, bins = train.H0Sample(i,params=params)
        out  = metrics.computeMetrics(P, tmpl, bins, maxTime)
        out += metrics.highFreqTemplate(P, bar_)
        out += metrics.highFreqTemplate(P, bar1_)
        out += metrics.highFreqTemplate(P, bar2_)
        #hL.append([0, i] + out)
        hL.append( (fid, [0,i]+out) ) # NOTE added fid for sorting below

    # NOTE Sort by fileID so metrics file lines are in 
    # sequential order (train1.aiff, train2.aiff....)
    print "\nsorting metrics by fileID"
    hL_sort = np.array( [metric_lst for fid, metric_lst in sorted(hL)] ) 

    print "writing metrics to:", trainOutFile
    file = open(trainOutFile,'w')
    file.write("Truth,Index,"+outHdr+"\n")
    np.savetxt(file,hL_sort,delimiter=',')
    file.close()
        

if __name__ == "__main__":
    main()
