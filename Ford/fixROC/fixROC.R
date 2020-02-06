library(ROCR)

TRAIN_FILE <- "/home/chefele/Ford/blendall/fordTrain.assembled.features.csv"
TEST_FILE  <- "/home/chefele/Ford/blendall/fordTest.assembled.features.csv"

TRAIN_OUT_FILE <- "fixROC.train.out.csv"
TEST_OUT_FILE  <- "fixROC.test.out.csv"
PLOTFILE       <- "fixROC.plots.pdf"

MIN.IMPROVEMENT <- 0.0250                          # min AUC improvement needed to include the ROC fix
NO_OPT_VARS <- c("TrialID","ObsNum","IsAlert")     #Variables not to fix 

# NUM_SAMPLES <- 10000   # *******

# -----------------------------------------

calcAUC <- function(predictions, labels) {  # uses ROCR library
                performance(prediction(predictions,labels), "auc")@y.values[[1]] 
} 

plotROC<- function(predictions, labels, plot.name) {
    # ROCR functions below
    plot(
        performance( 
            prediction(predictions,labels), measure = "tpr", x.measure = "fpr" 
        ), 
        main=plot.name
    )
}
pdf(file=PLOTFILE)


train <- read.csv(TRAIN_FILE)
test  <- read.csv(TEST_FILE)

# sample data for speed; use all data for final runs   ***********
# train <- train[ sample(1:nrow(train),NUM_SAMPLES),]
# test  <- test[  sample(1:nrow(test) ,NUM_SAMPLES),]

train.out <- data.frame(dummy=1:nrow(train))
train.out$dummy <- NULL
test.out <- data.frame(dummy=1:nrow(test))
test.out$dummy <- NULL

for(nm in names(train)) {

    print("**************************************************")
    print(nm)
    print("**************************************************")

    Y <- train$IsAlert

    if( nm %in% NO_OPT_VARS ) {   # skip some data (headers, etc) to not optimize  
        origX <- train[[nm]]
        origX.test <- test[[nm]]
    } else {
        # now convert data to percentiles, using combined distribution of test+train 
        train.and.test <- rbind( as.matrix(train[[nm]]), as.matrix(test[[nm]]) ) 
        origX      <- ecdf( train.and.test )( train[[nm]] )  
        origX.test <- ecdf( train.and.test )( test[[ nm]] )  
    } 

    origAUC <- calcAUC(origX,Y)   
    if( (origAUC<0.5) && !(nm %in% NO_OPT_VARS) ) {               # just flip ROC curve if AUC<0.5
        origX   <- 1-origX
        origX.test <- 1-origX.test
        origAUC <- 1-origAUC
    }
    bestX <- origX
    bestX.test <- origX.test
    bestAUC <- origAUC  
    
    if( !(nm %in% NO_OPT_VARS) ) {   # skip some data (headers, etc) to not optimize  
        # Optimize ROC & fix it via these loops 
        for(i in 0:9) {
            for(j in i:10) { 
                X <- origX * 1.0 
                X.test <- origX.test * 1.0 
                THRESH.LO <- i/10
                THRESH.HI <- j/10
                # to flip the concave ROC region, invert the range of values as follows
                mask <- (X<THRESH.HI) & (X>THRESH.LO)
                X[mask] <- THRESH.HI + THRESH.LO - X[mask]
                mask.test <- (X.test<THRESH.HI) & (X.test>THRESH.LO)
                X.test[mask.test] <- THRESH.HI + THRESH.LO - X.test[mask.test]

                fixAUC <- calcAUC(X,Y)
                if(fixAUC > bestAUC) {
                    bestAUC <- fixAUC
                    bestX   <- X
                    bestX.test <- X.test 
                } 
                print( paste(
                    "RESULT:  Var:", nm, 
                    "Fix_Gain: ", as.character(fixAUC-origAUC), 
                    "BEST_Gain: ", as.character(bestAUC-origAUC),
                    "Thresh: HI:", as.character(THRESH.HI), 
                    "LO:", as.character(THRESH.LO)
                    )
                )
            }
        }
    }
    # Now have optimum ROC curve data in bestX & bestX.test 

    print("")
    print( paste("FINAL_BEST_GAIN for: ", nm," = ", as.character(bestAUC-origAUC) ) ) 
    print("")

    if((bestAUC-origAUC) > MIN.IMPROVEMENT) {
        train.out[[nm]] <- bestX
        test.out[[nm]]  <- bestX.test
    } else {
        train.out[[nm]] <- train[[nm]]
        test.out[[nm]]  <- test[[nm]]
    }

    plotROC(
             data.frame(Original=origX, Fixed=bestX),  # predictions
             data.frame(Original=Y,     Fixed=Y),      # labels
             paste("Variable: ",nm,"     AUC_Improvement:", as.character(bestAUC-origAUC) )  
    ) 

} # end loop over names

train.out$TrialID <- train$TrialID
train.out$ObsNum  <- train$ObsNum
train.out$IsAlert <- train$IsAlert

test.out$TrialID <- test$TrialID
test.out$ObsNum  <- test$ObsNum
test.out$IsAlert <- test$IsAlert

write.csv(train.out, file=TRAIN_OUT_FILE, quote=FALSE, row.names=FALSE)
write.csv(test.out,  file=TEST_OUT_FILE , quote=FALSE, row.names=FALSE)


