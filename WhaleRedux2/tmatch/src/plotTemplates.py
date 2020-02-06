""" plotTemplates.py

    This file plots the templates
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

def main():
    # baseDir = '/home/nick/whale/' # Base directory
    baseDir     = globalConst.BASE_DIR

    ###################### SET OUTPUT FILE NAME HERE ########################
    trainOutFile = baseDir+'workspace/trainMetrics.csv'
    
    ############################## PARAMETERS ###############################
    dataDir         = baseDir+'data/'                  # Data directory
    templateDataDir = baseDir+'template_data/'         # Data directory

    params = {'NFFT':256, 'Fs':2000, 'noverlap':192} # Spectogram parameters
    maxTime = 60 # Number of time slice metrics

    ######################## BUILD A TrainData OBJECT #######################
    train         = fileio.TrainData(        dataDir+'train.csv',dataDir+'train/')
    templateTrain = fileio.TrainData(templateDataDir+'train.csv',templateDataDir+'train/')

    ##################### BUILD A TemplateManager OBJECT ####################
    tmplFile = baseDir+'moby/templateReduced.csv'
    tmpl = templateManager.TemplateManager(fileName=tmplFile, 
                                           trainObj=templateTrain, params=params)

    ##################### PLOT the templates  ####################
    for ix in range(tmpl.size):
        print "Plotting template:",ix
        tmpl.PlotTemplates(index=ix)

if __name__ == "__main__":
    main()
