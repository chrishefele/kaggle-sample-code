# rmse_split.R 
# usage:   Rscript rmse_split.R <testfile> 
# Calculates rmses of a simulated private/public leaderboard testset split

rmsle     <- function(p, a) { sqrt(mean((log(p+1)-log(a+1))^2)) }  #error function

LEADERBOARD_PUBLIC  <- 21000 # number of random samples used for public leaderboard
RANDOM_SEED         <- 1234567
set.seed(RANDOM_SEED)

args <- commandArgs(TRUE)
FILE1 <- args[1]
FILE2 <- args[2]
preds1 <- read.csv(FILE1)
preds2 <- read.csv(FILE2)

mask.public  <- preds1$MemberID %in%  sample(preds1$MemberID, LEADERBOARD_PUBLIC)
mask.private <- !mask.public
mask.overall <- mask.private | mask.public

rmse.public  <- rmsle(preds1$DaysInHospital[mask.public],  preds2$DaysInHospital[mask.public ])
rmse.private <- rmsle(preds1$DaysInHospital[mask.private], preds2$DaysInHospital[mask.private])
rmse.overall <- rmsle(preds1$DaysInHospital[mask.overall], preds2$DaysInHospital[mask.overall])

grep.tag <- paste("RES","ULTS:", sep="")
results  <- paste(   grep.tag, 
                    "public_RMSE: ",as.character(rmse.public), 
                    "private_RMSE:",as.character(rmse.private), 
                    "overall_RMSE:",as.character(rmse.overall),
                    # "file1:", FILE1,
                    # "file2:", FILE2,  
                    "\n"
           )

cat(results)

