MAE <- function(x, y) { mean(abs(x-y)) }

N        <- 1000

rands    <- sort(runif(N))
cat('rands::  median: ', median(rands), 
              ' mean: ', mean(rands), 
              ' diff: ', median(rands)-mean(rands), 
              '\n' )
mean.estimate <- 0

for(i in c(1:100)) {
    mae <- MAE(rands, mean.estimate)
    print(mae)
    mean.estimate <- mae
}









