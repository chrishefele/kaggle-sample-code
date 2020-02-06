# rmse.split.noheader.R 
# usage:   cat rmse.split.noheader.R | R --vanilla --args <PROBEFILE> 
# calculates rmses of a simulated private/public leaderboard testset split
# assumes no header on read predictions file

INFILE   <- commandArgs(trailingOnly=TRUE)[1]
DATA_DIR <- "/home/chefele/AlgoTrading/data/"
PREDICTION_TIMES <- 51:100

bid.names   <- paste("bid", as.character(PREDICTION_TIMES),sep="")
ask.names   <- paste("ask", as.character(PREDICTION_TIMES),sep="")
bidask.names<- as.vector(rbind(bid.names,ask.names))

load(paste(DATA_DIR, "probe.Rsave", sep="")) 
print(paste("Reading:", INFILE))
preds.probe  <- read.csv(INFILE, header=FALSE)
names(preds.probe) <- c("row_id", bidask.names)

#print(bidask.names)
#print(names(probe))
#print(names(preds.probe))

LEADERBOARD_PUBLIC  <- 15000 
LEADERBOARD_PRIVATE <- 35000
RANDOM_SEED <- 1234567

set.seed(RANDOM_SEED)
mask.public  <- probe$row_id  %in%  sample(probe$row_id, LEADERBOARD_PUBLIC)
mask.private <- !mask.public
mask.overall <- mask.private | mask.public

rmse <- function(preds, row.mask) { 
    errs <- as.matrix( preds[row.mask, bidask.names] - probe[row.mask, bidask.names] )
    sqrt(mean(errs*errs))
}

rmse.public  <- rmse(preds.probe, mask.public)
rmse.private <- rmse(preds.probe, mask.private)
rmse.overall <- rmse(preds.probe, mask.overall)
grep.tag <- paste("RES","ULTS:", sep="")
results <- paste(   grep.tag, 
                    "public_RMSE: ",as.character(rmse.public), 
                    "private_RMSE:",as.character(rmse.private), 
                    "overall_RMSE:",as.character(rmse.overall),
                    "file:", INFILE
           )

print(results)

