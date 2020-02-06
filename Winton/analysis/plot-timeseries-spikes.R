
PAGE.ROWS <- 3
PAGE.COLS <- 4
TOP.N     <- PAGE.ROWS * PAGE.COLS

pdf(file="plot-timeseries-spikes.pdf")
par(mfrow=c(PAGE.ROWS, PAGE.COLS))

train <- readRDS("../data/train.RData")
train[is.na(train)] <- 0 

ret.cols <- paste("Ret_", c(2:180), sep="")
cols.select <- c("Id", ret.cols)

for(spike.col in ret.cols) {

    norm.spike.size <- abs(train[,spike.col]) / rowMeans(abs(train[,ret.cols]))
    row.order <-  order(norm.spike.size, decreasing=TRUE)
    df <- train[row.order, cols.select]
    df <- df[1:TOP.N,]

    for(id in df$Id) {
        cat("plotting: ", spike.col, " Id ", id, "\n")
        tag <- paste(spike.col, "Id", id)
        tag.cs <- paste("Cum", tag)
        intraday.ret <- as.numeric( df[id==df$Id, ret.cols] ) 
        limit <- max(abs(intraday.ret))
        plot(intraday.ret, main=tag, type="l", ylim=c(-limit, limit))

        limit <- max(abs(cumsum(intraday.ret)))
        plot(cumsum(intraday.ret), main=tag, type="l", ylim=c(-limit, limit))
    }
}


