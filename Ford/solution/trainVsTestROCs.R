library(ROCR)

TRAIN_FILE <- "/home/chefele/Ford/download/fordTrain.csv"
TEST_FILE  <- "/home/chefele/Ford/download/fordTest.csv" 
TEST_SOLUTION_FILE <- "/home/chefele/Ford/download/fordTestSolution.csv"

PLOTFILE   <- "trainVsTestROCs.pdf"

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

test  <- read.csv(TEST_FILE)
test.soln  <- read.csv(TEST_SOLUTION_FILE)
test$IsAlert <- test.soln$Prediction

train <- read.csv(TRAIN_FILE)
train <- train[ sample(1:nrow(train),nrow(test)) , ]

for( nm in setdiff( names(train), c("TrialID", "ObsNum", "IsAlert") ) ) {
    train.auc <- round( calcAUC(train[[nm]],train$IsAlert),4)
    test.auc  <- round( calcAUC(test[[nm]], test$IsAlert ),4)
    auc.diff  <- round( abs(train.auc - test.auc), 4) 
    outstring <- paste( "Variable: ",nm, 
                     " Train_AUC=", as.character(train.auc),
                     " Test_AUC=",    as.character(test.auc ), 
                     " Gap=",  as.character(auc.diff ), 
                     sep=""
             )
    print(outstring)
    plotROC(
             data.frame( Train=train[[nm]],       Test=test[[nm]]  ),      # predictions
             data.frame( Train=train$IsAlert,     Test=test$IsAlert),      # labels
             outstring
    ) 
} # end loop over names


