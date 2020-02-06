
DATA_DIR      <- "/home/chefele/kaggle/HHP/features/"
TRAIN_ANALOG  <- paste(DATA_DIR,"Y1_xfeatures.csv",sep="")
TRAIN_ACTUALS <- paste(DATA_DIR,"Y1_xanswers.csv" ,sep="")

train_analog     <- read.csv(TRAIN_ANALOG)
train_actuals_df <- read.csv(TRAIN_ACTUALS)
train_actuals    <- (train_actuals_df$DaysInHospital > 0)*1

pdf("../results/nonzero_hists.pdf")
par(mfrow=c(2,2))   # (Rows,Cols) layout of multiple plots per page 

for(varName in names(train_analog)) {
    zdata  <- train_analog[[varName]]
    nzdata <- zdata[zdata>0]
    log.nzdata <- log(nzdata+1)
    hist( nzdata,     main=paste(varName, "Histogram, x>0"))
    hist( log.nzdata, main=paste(varName, "log(x+1) Histogram, x>0"))
    cat(varName)
    cat("\n")
}


