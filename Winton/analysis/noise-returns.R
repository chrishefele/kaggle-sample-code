
csv.data <- readRDS("../data/train.RData")

train.cols      <- paste("Ret_", as.character(c(2:180)), sep="")
train.returns   <- as.matrix(csv.data[,train.cols])
# train.returns[is.na(train.returns)] <- 0

EPS <- 10^-4.5
small.ret.count <- function(r) sum( r<EPS & r>-EPS, na.rm=TRUE ) 
small.ret.counts <- apply(train.returns, 1, small.ret.count)  

# hist(small.ret.counts, 100)

results <- data.frame(ID=csv.data$Id, count=small.ret.counts)

results.sort <- results[order(-small.ret.counts),]

gt100 <- results.sort$count > 100

print(results.sort[gt100,])


