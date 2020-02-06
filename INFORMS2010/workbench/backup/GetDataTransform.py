from Transforms import * 
from Transforms import _timeShift 
import numpy
from VariableSelection import AllPriceReturns # stock_prices -> return permutations

def getDataTransform(dataTransformName, providedDataObject):
    pd = providedDataObject

    targetVariable      = pd.getTargetVar()
    timestamps          = pd.getTimestamps()
    getFloatVars        = makeGetFloatVars(pd.getFloatData)
    getFloatPriceVars   = makeGetFloatPriceVars(pd.getFloatPriceData) 
    getCategoricalVars  = makeGetCategoricalVars(pd.getIntData)
    var74Selector       = makeSelectVars( "Variable74_LASTLASTRETURN")

    var74PriceSelector  = makeSelectVars(["Variable74OPEN", "Variable74HIGH", \
                                          "Variable74LOW",  "Variable74LAST_PRICE"])
    var55PriceSelector  = makeSelectVars(["Variable55OPEN", "Variable55HIGH", \
                                          "Variable55LOW",  "Variable55LAST_PRICE"])
    var112PriceSelector = makeSelectVars(["Variable112OPEN", "Variable112HIGH", \
                                          "Variable112LOW",  "Variable112LAST_PRICE"])
    var112PriceSelector = makeSelectVars(["Variable112OPEN", "Variable112LOW"])

    var74HighSelector   = makeSelectVars(["Variable74HIGH"])
    var74LowSelector    = makeSelectVars(["Variable74LOW" ])
    var74Shift1         = makeMultiTimeShiftVars([ 1])
    var74Shift13        = makeMultiTimeShiftVars([13])
    var74PriceTimeShifts= makeMultiTimeShiftVars([1,13])
    varPriceLags0       = makeMultiTimeShiftVars([0,12])
    varPriceLags1       = makeMultiTimeShiftVars([1,13])
    varPriceLags2       = makeMultiTimeShiftVars([2,14])

    getTimeOfDayMeanTargetVar = makeGetTimeOfDayMeanTargetVar(timestamps, targetVariable)
    periodNorm          = makePeriodNorm(timestamps)
    getTimeBinVars      = makeGetTimeBinVars(timestamps)
    doAnchoredPCAVar74  = makeDoAnchoredPCA("Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD")

    #  Other available preprocessing functions (from Transform.py) 
    #  centerMean(inData):
    #  normStd(inData):
    #  normCenter(inData):
    #  normZeroToOne(inData):
    #  squareVars(inData):
    #  cubeVars(inData):
    #  cubicPolynomialVars(inData):
    #  signVars(inData):
    #  entropyOfProbs(inData):
    #  percentileVars(inData):
    #  percentileToGaussian(inData):
    #  timeShiftedOnlyVars(inData):  #doesn't include original vars, only the shifts
    #  timeShiftVars(inData):        #shifted vars, along with the original vars 
    #  fullCrossProduct(inData):
    #  makePartialCrossProduct(inDataOne) & partialCrossProduct(inDataTwo):
    #  doPCA(inData):
    #  doICA(inData):
    #  integrateVars(inData):
    #  gradientVars(inData):
    #  diffVars(inData):

    d = {} 
    d['passthruVars'] = [[[passthruVars]]]
    d['normCenter'] = [[[normCenter]]]
    d['periodNorm'] = [[[periodNorm]]]
    d['percentileVars'] = [[[percentileVars]]]
    d['timeOfDay'] = [[[getTimeOfDayMeanTargetVar],[passthruVars]]]

    d['crossProduct-normCenter'] =      [[[normCenter], [fullCrossProduct, normCenter]]]
    d['crossProduct-normZeroToOne'] =   [[[normZeroToOne], [fullCrossProduct, normZeroToOne]]]
    d['crossProduct-percentileVars'] =  [[[percentileVars], [fullCrossProduct, percentileVars]]]
    d['cubicpoly'] = [[[cubicPolynomialVars]]]
    d['cubicpoly-v74'] = \
        [[[normCenter, cubicPolynomialVars, normCenter, var74Selector, getFloatVars]]]
    d['entropy-norm01'] = [[[entropyOfProbs, normZeroToOne],[normZeroToOne]]]
    d['normCenter-floats']     = [[[normCenter, getFloatVars]]]
    d['normStd-floats']= [[[normStd, getFloatVars]]]
    d['normStd-v74']= [[[normStd, var74Selector, getFloatVars]]]
    d['pca-floats'] = [[[normCenter, doPCA, normCenter, getFloatVars]]]
    d['ica-floats'] = [[[normCenter, doICA, normCenter, getFloatVars]]]
    d['tod'] = [[[getTimeOfDayMeanTargetVar]]] #auc 0.5495 with linreg

    d['int-v74']    = [[[normCenter, integrateVars, normCenter, var74Selector, getFloatVars]]]
    d['int-floats'] = [[[normCenter, integrateVars, normCenter, getFloatVars]]]
    d['grad-v74']   = [[[normCenter, gradientVars,  normCenter, var74Selector, getFloatVars]]]
    d['grad-floats']= [[[normCenter, gradientVars,  normCenter, getFloatVars]]]
    d['grad-catvars'] = [[[normCenter, gradientVars,  normCenter, getCategoricalVars]]]
    d['int-catvars'] = [[[normCenter, integrateVars,  normCenter, getCategoricalVars]]]

    # best combination found so far progression below =========

    d['nc-gfv'] = \
        [[[                normCenter, getFloatVars ]]]
    d['tsv-nc-gfv'] = \
        [[[ timeShiftVars, normCenter, getFloatVars ]]]

    d['nc-v74-gfv'] = \
        [[[                             normCenter, var74Selector, getFloatVars ]]]
    d['tsv-nc-v74-gfv'] = \
        [[[              timeShiftVars, normCenter, var74Selector, getFloatVars ]]]
    d['pn-tsv-nc-v74-gfv'] = \
        [[[   periodNorm, timeShiftVars, normCenter, var74Selector, getFloatVars ]]]
    d['pv-pn-tsv-nc-v74-gfv'] = \
        [[[percentileVars, periodNorm, timeShiftVars, normCenter, var74Selector, getFloatVars ]]]
    d['nc-pv-pn-tsv-nc-v74-gfv'] = \
        [[[normCenter, percentileVars, periodNorm, timeShiftVars, normCenter, \
                                                            var74Selector, getFloatVars ]]]
    d['gtodmtv+nc-pv-pn-tsv-nc-v74-gfv'] = \
        [[[getTimeOfDayMeanTargetVar], \
         [normCenter, percentileVars, periodNorm, timeShiftVars, normCenter, \
                                                            var74Selector, getFloatVars]]]
    d['best'] = d['gtodmtv+nc-pv-pn-tsv-nc-v74-gfv']

    # ===================

    d['v74'] = d['nc-v74-gfv'] # simpler alias 

    # for coint experiments; gets 0.9671 in L2 & L1 
    d['nc-pn-nc-v74-gfv'] = \
        [[[normCenter, periodNorm, normCenter, var74Selector, getFloatVars]]]
    d['cointbest'] = d['nc-pn-nc-v74-gfv'] # alias 


    
    # Variable 74 Raw Prices Experiments
    d['normCenter-v74prices'] = [[[normCenter, var74PriceSelector, getFloatVars]]]
    d['v74shifts-normCenter-v74prices'] = \
          [[[var74PriceTimeShifts, normCenter, var74PriceSelector, getFloatVars]]]
    d['v74prices-hi1-low13'] = \
          [[[var74Shift1,  normCenter, var74HighSelector, getFloatVars],\
            [var74Shift13, normCenter, var74LowSelector,  getFloatVars]]]
    d['v74prices-hi1-low13-best'] = \
          [[[var74Shift1,  normCenter, var74HighSelector, getFloatVars],\
            [var74Shift13, normCenter, var74LowSelector,  getFloatVars]]]

    # all variable raw price experiments; need lags, and subtract to get returns...
    d['normCenter-allPrices'] = [[[normCenter, getFloatPriceVars]]]
    d['getFloatPriceVars']    = [[[getFloatPriceVars]]]
    d['getVar74PriceVars']    = [[[var74PriceSelector, getFloatVars]]]

    # -------------------------------------------------------------------------
    def makeVar74ReturnCombo(startSuffix, endSuffix, startShift, endShift):
        def var74ReturnCombo(inData): # convert raw_prices->returns 
            outData = {} 
            startData = _timeShift(inData["Variable74"+startSuffix],startShift)
            endData   = _timeShift(inData["Variable74"+endSuffix],endShift)
            # returns = endData - startData
            returns = numpy.log10(endData) - numpy.log10(startData)
            returnSuffix = startSuffix+str(startShift)+endSuffix+str(endShift)
            outData["Variable74"+returnSuffix] = returns 
            print "RETURN_COMBINATION:", returnSuffix
            return outData
        return var74ReturnCombo

    def var74PriceCombinations():
        var74Suffixes = ["OPEN","HIGH","LOW","LAST_PRICE"]
        startShiftList = [-2,-1,0,1,2]
        endShiftList = [11,12,13,14,15]
        transformsList = []
        for startSuffix in var74Suffixes:
            for endSuffix in var74Suffixes:
                for startShift in startShiftList:
                    for endShift in endShiftList:
                        v74ReturnCombo = makeVar74ReturnCombo(\
                                    startSuffix, endSuffix, startShift, endShift)
                        transformsList.append([[normCenter, v74ReturnCombo, getFloatVars]]) 
        print "Generated:",len(transformsList),"Var74 price combinations"
        return transformsList
    d['var74PriceCombinations'] = var74PriceCombinations()
    # -------------------------------------------------------------------------


    d['sept21trial1'] = \
        [[[ percentileVars, periodNorm, timeShiftVars, \
            normCenter, var74Selector, getFloatVars ]]]

    def makeVarPriceReturns(inData, varNumNameStart, startLag, varNumNameEnd, endLag): 
        startData = _timeShift( inData[varNumNameStart],startLag)
        endData   = _timeShift( inData[varNumNameEnd],  endLag)
        returns = numpy.log10(endData) - numpy.log10(startData)
        returnsName = varNumNameEnd   + "_LAG"+str(endLag) + "_-_" +\
                      varNumNameStart + "_LAG"+str(startLag)
        return { returnsName : returns }

    def makeVar74PriceReturns(inData):
        var74pr1 = makeVarPriceReturns(inData, "Variable74HIGH",       1, \
                                               "Variable74LOW",       13)
        var74pr2 = makeVarPriceReturns(inData, "Variable74LAST_PRICE", 0, \
                                               "Variable74LAST_PRICE",12)
        return dict( var74pr1.items() + var74pr2.items() ) 

    # the following got a NEW HIGH on leaderboard of 0.978796
    # kfold AUC: 0.9675  public AUC: 0.978796 Gap: 0.0113
    d['sept22trial1'] = [[[normCenter, makeVar74PriceReturns, getFloatPriceVars]]] 

    # kfold AUC: 0.96878  public AUC: 0.979726 Gap: 0.0109
    d['sept23trial1']=[[[normCenter, varPriceLags0, var74PriceSelector, getFloatPriceVars],\
                        [normCenter, varPriceLags1, var74PriceSelector, getFloatPriceVars]]]

    # kfold AUC:  0.96924   public AUC: 0.980036 Gap: 0.0108
    d['sept23trial2']=[[[normCenter, varPriceLags0, var74PriceSelector, getFloatPriceVars],\
                        [normCenter, varPriceLags1, var74PriceSelector, getFloatPriceVars],\
                        [normCenter, varPriceLags0, var55PriceSelector, getFloatPriceVars]]]
    # TO DO:  only use price/lag combos selected by varselect; prune other prices out


    # testing use of svm on a big set of data 
    #d['bigsvm'] = [[[normCenter, AllPriceReturns, var74PriceSelector, getFloatPriceVars]]]
    d['bigsvm']  = [[[normCenter, AllPriceReturns,                     getFloatPriceVars]]]

    # sharpened features from sept23trial2
    # kfold AUC: 0.97012 public AUC: 0.978858 Gap:  0.00874  (LESS overfit??) 
    d['sept28trial1'] = [[\
        [ normCenter, makeVarSelectLag("Variable74LOW", 13),        getFloatPriceVars],\
        [ normCenter, makeVarSelectLag("Variable74HIGH", 1),        getFloatPriceVars],\
        [ normCenter, makeVarSelectLag("Variable74LAST_PRICE", 12), getFloatPriceVars],\
        [ normCenter, makeVarSelectLag("Variable74LAST_PRICE",  0), getFloatPriceVars],\
        [ normCenter, makeVarSelectLag("Variable55LAST_PRICE", 12), getFloatPriceVars],\
        [ normCenter, makeVarSelectLag("Variable55HIGH",  0),       getFloatPriceVars] \
        ]]

    # initial --transform 
    d['sept28prices']        = [[[getFloatPriceVars]]]
    # for --returntransform 
    d['sept28retpassthru']   = [[[passthruVars]]]
    d['sept28retpct']        = [[[percentileVars]]]
    d['sept28retnormperiod'] = [[[makePeriodNorm(timestamps)]]]
    d['sept28retpctnormperiod'] = [[[ percentileVars, makePeriodNorm(timestamps) ]]]
    d['sept28retnormperiodpct'] = [[[ makePeriodNorm(timestamps), percentileVars ]]]
    # retpctnormperiod had the biggest gains by far (percentileVars of periodNorm) 


    # CONCLUSION of below:  1-Hour Min/Max of Hi/Lo prices has NO benefit
    d['sept29minmaxbaseline'] = [[[ var74PriceTimeShifts, \
                                    var74PriceSelector, getFloatPriceVars]]]
    d['sept29minmaxtest'] =     [[[ var74PriceTimeShifts, \
                                    appendHourMinMaxHighLowPriceVars, \
                                    var74PriceSelector, getFloatPriceVars]]]
    d['sept29vsmm1'] = [[[  var74PriceSelector, getFloatPriceVars ]]]
    d['sept29vsmm2'] = [[[  appendHourMinMaxHighLowPriceVars,\
                            var74PriceSelector, getFloatPriceVars ]]]

    # sept 30 experiments with hourSlopeVars and hourCorrVars 
    # conclusion: might help a little ~0.0010 when in parallel with other variables
    d['sept30Prices']           = [[[   normCenter, makeMultiTimeShiftVars([0,1,12,13]), \
                                        var74PriceSelector, getFloatPriceVars ]]]
    d['sept30Returns']          = [[[   normCenter, makeMultiTimeShiftVars([0,1]),\
                                        var74Selector, getFloatVars]]]
    d['sept30hourSlopeVars']    = [[[   normCenter, makeMultiTimeShiftVars([0,1]),\
                                        hourSlopeVars, \
                                        var74PriceSelector, getFloatPriceVars ]]]
    d['sept30hourCorrVars']     = [[[   normCenter, makeMultiTimeShiftVars([0,1]),\
                                        hourCorrVars, \
                                        var74PriceSelector, getFloatPriceVars ]]]
    d['sept30ReturnsHourSlopeVars'] = [[ d['sept30Returns'][0][0], \
                                         d['sept30hourSlopeVars'][0][0]  ]]
    d['sept30ReturnsHourCorrVars']  = [[ d['sept30Returns'][0][0], \
                                         d['sept30hourCorrVars'][0][0]   ]]
    
    # item  below for --transform 
    d['sept30varSelectInputPrices']      =   [[[getFloatPriceVars]]] 
    d['sept30varSelectInputPricesTEST']  =   [[[var74PriceSelector, getFloatPriceVars]]]
    # items below for  --etcreturntransform 
    d['sept30hourSlopeVarsTEST']= [[[makeMultiTimeShiftVars([0,1]),\
                                 hourSlopeVars,var74PriceSelector, getFloatPriceVars]]]
    d['sept30hourSlopeVars']= [[[makeMultiTimeShiftVars([0,1]),\
                                 hourSlopeVars,getFloatPriceVars]]]
    d['sept30hourCorrVars'] = [[[makeMultiTimeShiftVars([0,1]),\
                                 hourCorrVars, getFloatPriceVars]]]
    # --returntransform
    d['sept30PercentileNormPeriod'] = [[[ percentileVars, makePeriodNorm(timestamps) ]]]


    # for varselect --transform
    d['Oct1Prices']       =   [[[getFloatPriceVars]]] 
    d['Oct1Var74Prices']  =   [[[var74PriceSelector, getFloatPriceVars]]]
    # for varselect --returntransform
    d['Oct1pct']         = [[[                        percentileVars ]]] #baseline
    d['Oct1PCApct']      = [[[                 doPCA, percentileVars ]]] #worse  0.0002 v74
    d['Oct1pctPCA']      = [[[ percentileVars, doPCA                 ]]] #worse  0.0006 v74
    d['Oct1pctPCApct']   = [[[ percentileVars, doPCA, percentileVars ]]] #better 0.0005 v74


    def Oct3Definitions():
        outData = {}
        pct = percentileVars
        pnm = periodNorm
        nmc = normCenter
        pca = doPCA
        for f2name,f2,f4name,f4 in [("pca",pca,"pnm",pnm),("pnm",pnm,"pca",pca)]:
            for f1name,f1 in [("nmc",nmc),("pct",pct)]:
                for f3name, f3 in [("nmc",nmc),("pct",pct)]:
                    for f5name, f5 in [("nmc",nmc),("pct",pct)]:
                        name = "Oct3_"+f1name+"_"+f2name+"_"+f3name+"_"+f4name+"_"+f5name
                        funcList = [[[f1,f2,f3,f4,f5]]]
                        outData[name] = funcList
                        print "Defined:",name
        return outData

    # for varselect --transform
    d['Oct3Prices']       = [[[getFloatPriceVars]]] 
    d['Oct3Var74Prices']  = [[[var74PriceSelector, getFloatPriceVars]]]
    # for varselect --returntransform 
    d['Oct3baseline']     = [[[ percentileVars, periodNorm ]]] # add doPCA
    d = dict( d.items() + Oct3Definitions().items() ) 


    # varselect --transform
    d['Oct4Prices']       = [[[getFloatPriceVars]]] 
    d['Oct4Var74Prices']  = [[[var74PriceSelector, getFloatPriceVars]]]
    # varselect --returntransform
    d['Oct4Baseline'] = [[[ percentileVars, makePeriodNorm(timestamps) ]]] #from sep28
    d['Oct4Trial']    = [[[ percentileVars, makePeriodNorm(timestamps), \
                            normCenter, doPCA, percentileVars ]]]
    d['Oct4Trial2']   = [[[ percentileVars, makePeriodNorm(timestamps), \
                            normCenter, doICA, percentileVars ]]]
    d['Oct4Trial3']    = [[[ percentileVars, makePeriodNorm(timestamps), \
                             normCenter, percentileVars ]]]
    d['Oct4Trial4']    = [[[ percentileVars, makePeriodNorm(timestamps), \
                             normCenter ]]]
    # TRIAL 3 was the best on Var74 only (pass1/9668) (2/9697) (3/9698) 
    # Baseline3 on Var74 only was :      (pass1/9659) (2/9694) (3/9692) 


    # Multiple Gradient Experiement 
    # baseline got 0.9539 kfold
    d['Oct5GradientsBaseline'] = [[[ normCenter, var74Selector, getFloatVars ]]]
    def makeOct5Gradients():
        outList=[]
        for n in range(15):
            outList.append( [normCenter] + n*[gradientVars] + [var74Selector,getFloatVars] ) 
        return [outList] 
    d['Oct5Gradients'] = makeOct5Gradients() # got 0.9594 AUC! big gain
    #TODO: add gradients???


    # Try various pre/post processors on period norm
    # for VarSelect: 
    #   --returntransform Oct5ProcComboN  N=1...25
    #   --transform Oct5Var74Prices 
    d['Oct5ProcComboBaseline'] = d['Oct4Trial3']  
    d['Oct5Var74Prices']  = [[[var74PriceSelector, getFloatPriceVars]]]
    def makeOct5ProcCombos():
        outData = {}
        comboNum = 0 
        processors = [ [passthruVars],[percentileVars],[normCenter],\
                       [percentileVars,normCenter],[normCenter,percentileVars] ] 
        for preProcessor in processors:
            for postProcessor in processors:
                comboNum += 1 
                transform = postProcessor + [makePeriodNorm(timestamps)] + preProcessor 
                outData['Oct5ProcCombo'+str(comboNum)] = [[transform]]
        return outData
    d = dict( d.items() + makeOct5ProcCombos().items() )
    _Oct5Baseline = [percentileVars, makePeriodNorm(timestamps),normCenter,percentileVars]
    d['Oct5Gradient0'] = [[_Oct5Baseline]]
    d['Oct5Gradient1'] = [[_Oct5Baseline,_Oct5Baseline+[gradientVars]]]
    d['Oct5Gradient2'] = [[_Oct5Baseline,_Oct5Baseline+[gradientVars],\
                                         _Oct5Baseline+[gradientVars,gradientVars]]]
    d['Oct5NoCrossProducts']     = [[_Oct5Baseline]]
    d['Oct5PostCrossProducts']   = [[_Oct5Baseline,[fullCrossProduct]+_Oct5Baseline]]
    d['Oct5PctPostCrossProducts'] = [[_Oct5Baseline,[percentileVars, fullCrossProduct]+_Oct5Baseline]]
    d['Oct5PreCrossProducts']    = [[_Oct5Baseline,_Oct5Baseline+[fullCrossProduct]]]


    # ========================================
    # Transform for VariableSelection
    # --transform
    d['Oct6AllVarPrices']   = [[[                       getFloatPriceVars]]] 
    d['Oct6Var74Prices']    = [[[var74PriceSelector,    getFloatPriceVars]]]
    _finalVarPriceSelector = makeSelectVars([ \
        "Variable74OPEN",  "Variable74HIGH",  "Variable74LOW",  "Variable74LAST_PRICE",\
        "Variable175LAST",\
        "Variable165OPEN", "Variable165LAST",\
        "Variable112OPEN", "Variable112HIGH", "Variable112LOW",  "Variable112LAST_PRICE",\
    ])
    d['Oct6FinalVarPrices'] = [[[_finalVarPriceSelector, getFloatPriceVars]]]
    # --returntransform
    d['Oct6FinalTransform'] = \
        [[[percentileVars, makePeriodNorm(timestamps),normCenter,percentileVars]]]

   
    return d[dataTransformName] 


