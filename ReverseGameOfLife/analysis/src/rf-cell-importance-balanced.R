# rf.R
#
# Runs a random forest for determining inter-cell influence 
# 
# Rscript rf-cell-importance-balanced.R --args [PLOT_OPTION=1|2|3]
#

library('randomForest')

args <- commandArgs(trailingOnly = TRUE) 
plotnum <- as.integer( args[2] ) 

TRAINING_FILE   <- "../../download/train.csv"
#PLOT_FILE       <- "rf-cell-importance-balanced.pdf"
PLOT_FILE       <- paste("rf-cell-importance-balanced-plot", as.character(plotnum), ".pdf", sep="")
DELTAS          <- c(1:5)
NTREE           <- 200 
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

        # create a balanced dataset, since about ~6X more cell=0 states than cell=1
        y1.rows <-         which(startCells[,ycol]==1)
        y0.rows <- sample( which(startCells[,ycol]==0), length(y1.rows) )
        y.rows  <- sample( c(y1.rows, y0.rows) ) # randomly permute order
        x.balanced <- x[y.rows,]
        y.balanced <- startCells[y.rows,ycol]  
        y.balanced <- as.factor(y.balanced)

        cat("\nPROCESSING CELL:", ycol, "DELTA:", delta, "\n")

        rf <- randomForest(x.balanced, y.balanced, 
                    ntree=NTREE, nodesize=TREE_NODE_SIZE, 
                    importance=TRUE, do.trace=TRUE ) 

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
        if(plotnum==1) {
            plotBoard( rf.imp$"0", paste("0_class",tag))
            plotBoard( rf.imp$"1", paste("1_class",tag))
        }
        if(plotnum==2) {
            plotBoard( rf.imp$MeanDecreaseAccuracy, paste("Accuracy", tag))
            plotBoard( rf.imp$MeanDecreaseGini, paste("Gini", tag))
        }
        if(plotnum==3) {
            plotBoard( log(rf.imp$MeanDecreaseGini + 0.01), paste("LogGini", tag)) # NOTE duplicate to round out page
            plotBoard( log(rf.imp$MeanDecreaseGini + 0.01), paste("LogGini", tag)) # NOTE duplicate to round out page
        }

    }
}

