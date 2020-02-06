
library(quantreg)

train <- readRDS("../data/train.RData")

t.range <- c(2:180)
returns.cols <- paste("Ret", as.character(t.range), sep="_")
sort.key <- "Feature_7"
train <- train[order(train[,sort.key]),]

for(row.num in 1:nrow(train)) {

    row.id         <- as.numeric(train[row.num, "Id"])
    sort.key.value <- as.numeric(train[row.num, sort.key])

    returns <- as.numeric(train[row.num, returns.cols])
    returns[is.na(returns)] <- 0
    if(all(is.na(returns))) { 
        next 
    }

    n <- length(returns)
    xt <- returns[1:n-1]
    yt <- returns[2:n]

    lm.model <- lm(yt~xt)
    lm.slope <- round( coef(lm.model)[["xt"]], digits=3)

    rq.model <- rq(yt~xt)
    rq.slope <- round( coef(rq.model)[["xt"]], digits=3)
    
    cat("row: ", row.num, " row.id: ", row.id)
    cat(" f7: ", sort.key.value)
    cat(" lm.slope: ", lm.slope)
    cat(" rq.slope: ", rq.slope)
    cat("\n")

}



