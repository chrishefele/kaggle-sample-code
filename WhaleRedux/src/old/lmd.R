library(TTR)
source('aucroc.R')

train <- read.csv('../features/filename_features_train.csv')
a <- 1- 1*(train$daymsec_pos0 == '0')
b <- 1- 1*(train$whale        == '0')

for(MOVING_AVG_LENGTH  in c(10,20,30,40,50,60,70,80,90,100,120,140,160,180,200,225,250,275,300,500,1000)) {

    a_sma <- SMA(a, n=MOVING_AVG_LENGTH)
    nowhale_mask <- a==0
    a_improved <- a
    a_improved[nowhale_mask] <- a_sma[nowhale_mask]

    cat("MA length:", MOVING_AVG_LENGTH, "ImprovedAUC:", calcAUC(a_improved, b), "\n")
}
