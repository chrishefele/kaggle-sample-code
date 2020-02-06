library(glmnet)
library(caTools)

probe <- read.csv("blend.probe.csv")
test  <- read.csv("blend.test.csv")

make.X.matrix <- function(inData) {
    outData <- data.frame( 
        inData$bsvd.Pred,
        log(inData$AdamicAdar+1),                           
        log(inData$AdamicAdarNeighborsNeighbors+1),         
        # log(inData$Jaccard+1),                              
        # log(inData$JaccardNeighborsNeighbors+1),
        log(inData$reversed_JaccardNeighborsNeighbors+1),   
        log(inData$OutnodeDegree),                      
        log(inData$OutnodeInvDegree),                     
        log(inData$PrefAttachment),                       
        log(inData$numAllNeighborsNeighbors+1),             
        log(inData$numCommonNeighbors+1),                   
        log(inData$numCommonNeighborsNeighbors+1),          
        log(inData$reversed_AdamicAdarNeighborsNeighbors+1),
        log(inData$reversed_numAllNeighborsNeighbors+1),   
        log(inData$reversed_numCommonNeighborsNeighbors+1)
    )
    return(as.matrix(outData))
}

X.test  <- make.X.matrix(test)
X.probe <- make.X.matrix(probe)
Y.probe <- probe$Prob

system.time( fit.probe <- cv.glmnet(X.probe, Y.probe, type.measure="auc", family="binomial") )
print(fit.probe)
coef(fit.probe)
plot(fit.probe)
summary(fit.probe)

# check AUC of cv-fit against known probe values 
Y.probe.pred   <- predict(fit.probe,newx=X.probe,s="lambda.min")
probeAUC <- colAUC( data.frame(Y.probe.pred,probe$bsvd.Pred), Y.probe) 
print(probeAUC)



