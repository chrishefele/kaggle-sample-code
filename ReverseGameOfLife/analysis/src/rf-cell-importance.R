# rf.R
#
# Runs a random forest for determining inter-cell influence 
#

library('randomForest')

TRAINING_FILE   <- "../../download/train.csv"
PLOT_FILE       <- "rf-cell-importance.pdf"
DELTAS          <- c(1:5)
NTREE           <- 100 # 500? 
TREE_NODE_SIZE  <- 20
RND_SEED        <- 12345678

set.seed(RND_SEED)
pdf(file=PLOT_FILE)
par(mfrow=c(2,2))

plotBoard <- function(board, tag) {
    board <- board[1:400]
    dim(board) <- c(20,20)
    board <- board[,20:1]
    image(board, main=tag)
    persp(board, xlab='board rows', ylab='board columns',
          zlab='importance', theta=30, phi=30, main=tag)
}

# get column names (ycols) for 1/8th of the full square 
# (due to fold/mirror symetries, only 55 cells needed))
ycols <- c(1:400) 
dim(ycols) <- c(20,20)
ycols <- ycols[1:10, 1:10]
mask <- lower.tri(ycols, diag=TRUE) 
ycols <- paste("start.", as.character(ycols[mask]), sep="")

cat("\nReading:", TRAINING_FILE, "\n")
training <- read.csv(TRAINING_FILE) # id, delta, start.1-start.400, stop.1-stop.400

for(delta in DELTAS) {

    startCells <- training[ training$delta==delta, grep("start", names(training))]
    stopCells  <- training[ training$delta==delta, grep("stop",  names(training))]

    # randomly permute each row seperately to create dummy "noise" variables that 
    # are useful for detecting statistical significance of varaible importance
    randCells  <- data.frame(t(apply(stopCells,1,sample)))  
    names(randCells) <- paste("RAND.", names(stopCells), sep="")
    randCells  <- randCells[,1:40]

    x  <- cbind(stopCells, randCells)

    for(ycol in ycols) {

        cat("\nPROCESSING CELL:", ycol, "DELTA:", delta, "\n")
        y  <- as.factor( startCells[,ycol] )

        # TODO balanced, stratified sampling from 0/1 classes? 

        rf <- randomForest(x, y, ntree=NTREE, nodesize=TREE_NODE_SIZE, importance=TRUE, do.trace=TRUE) 

        cat("\nERROR RATES for CELL:", ycol, "DELTA:", delta, "\n") 
        print(rf$err.rate)
        # print(paste("MIN_ERROR:", as.character(min(rf$err.rate))))

        cat("\nSORTED VARIABLE IMPORTANCE for CELL:", ycol, "DELTA:", delta, "\n") 
        rf.imp <- as.data.frame(importance(rf))
        sort.field <- "MeanDecreaseAccuracy"
        rf.imp.sort <- rf.imp[ order(rf.imp[[sort.field]], decreasing=TRUE) , ]
        print(rf.imp.sort)

        cat("\nVARIABLE IMPORTANCE for CELL:", ycol, "DELTA:", delta, "\n") 
        print(rf.imp)

        tag <- paste(ycol, "delta", as.character(delta))
        plotBoard( rf.imp$"0", paste("0_class",tag))
        plotBoard( rf.imp$"1", paste("1_class",tag))
        plotBoard( rf.imp$MeanDecreaseAccuracy, paste("Accuracy", tag))
        plotBoard( rf.imp$MeanDecreaseGini, paste("Gini", tag))
        plotBoard( log(rf.imp$MeanDecreaseGini + 0.01), paste("LogGini", tag)) # NOTE duplicate to round out page
        plotBoard( log(rf.imp$MeanDecreaseGini + 0.01), paste("LogGini", tag)) # NOTE duplicate to round out page

    }
}

