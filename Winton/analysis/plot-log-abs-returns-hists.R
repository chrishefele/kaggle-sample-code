library(ggplot2)

train <- readRDS("../data/train.RData")

pdf(file="plot-log-abs-returns-hists.pdf")

par(mfrow=c(2,2))

for(col in names(train)) {

    if(!grepl("Ret_", col, fixed=TRUE)) next

    cat("plotting: ", col,"\n")
    x.df <- data.frame(x=train[,col])
    x <- x.df$x
    x <- x[!is.na(x)]
    x <- x[abs(x)>0] 
    log.abs.return <- log10(abs(x))
    hist(log.abs.return, 100, main=paste("log10(abs(", col, ")"))

    g.hist <- ggplot(x.df, aes(x = x)) + 
              geom_histogram() + 
              #scale_x_log() +
              labs(title=col)
    # print(g.hist)
}


