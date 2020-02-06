# rrf.R
#
# Runs a regularized random forest for feature selection 
#
# usage:  cat rrf.R | R --vanilla --args <features_file>  

library('RRF')
source('rrfcv_fixed.R')

TRAINING_FILE <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
FEATURES_FILE <- commandArgs( trailingOnly=TRUE )[1] # features derived from training data
PLOT_FILE     <- 'rrf_plot.pdf'
NTREE         <- 500

features   <- read.csv(FEATURES_FILE)
training   <- read.delim(TRAINING_FILE, quote="")
essay_sets <- sort(unique(features$essay_set))
pdf(file=PLOT_FILE)

essay_sets <- c(1)  # for testing 
essay_set  <- 1

#for(essay_set in essay_sets) { 

# 4 < node_size < 32 seems optimal.  Perhaps just use 20. 

    x <- features[features$essay_set == essay_set,]
    y <- training[training$essay_set == essay_set, 'domain1_score']
    # rrf <- RRF(x,y, nodesize=node_size, ntree=NTREE, importance=TRUE, do.trace=TRUE, coefReg=0.8   )

    #print(rrf$importance)
    #plot(rrf)
    #varImpPlot(rrf)
    #print(varUsed(rrf))

    # ERR MSG when using the original rrfcv:
    #    Error in cut.default(trainy, c(-Inf, quantile(trainy, 1:4/5), Inf)) : 'breaks' are not unique
    # so created rrfcv_fixed.R to make it work, which is imported up front 

    # rr <- rrfcv.result <- rrfcv(x, y, cv.fold=5, step=0.9, do.trace=TRUE, ntree=NTREE)
    # plot(rr$n.var, rr$error.cv, log="x", type="o", lwd=2)
    tuneRRF(x, y, mtryStart=20, trace=TRUE, plot=TRUE)

#}


