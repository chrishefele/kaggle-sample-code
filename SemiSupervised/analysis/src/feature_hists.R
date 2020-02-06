
# plot histograms of 100 feature variables 

DATA_DIR <- "/home/chefele/SemiSupervised/data/data/"
TRAIN_BINARY <- paste(DATA_DIR,"bsvd_features_train.csv",sep="")
TRAIN_ANALOG <- paste(DATA_DIR,"train_analog.csv",sep="")

train_binary <- read.csv(TRAIN_BINARY,header=FALSE)
train_analog <- read.csv(TRAIN_ANALOG,header=FALSE)

pdf("feature_hists.pdf")
par(mfrow=c(4,3))   # (Rows,Cols) layout of multiple plots per page 

for(varName in names(train_binary)) {
    print(varName)
    hist( train_binary[[varName]], main=paste("Binary:",varName), xlim=c(-1.5,2.5), 100)
}

for(varName in names(train_analog)) {
    print(varName)
    hist( train_analog[[varName]], main=paste("Analog:",varName), 100)
}


