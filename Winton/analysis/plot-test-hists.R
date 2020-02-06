library(ggplot2)

train <- readRDS("../data/test.RData")

pdf(file="plot-test-hists.pdf")

par(mfrow=c(2,2))

for(col in names(train)) {
    cat("plotting: ", col,"\n")
    x.df <- data.frame(x=train[,col])
    hist(    x.df$x,  100, main=col)
    #hist(log(x), 100, main=paste("log10", col) )

    g.hist <- ggplot(x.df, aes(x = x)) + 
              geom_histogram() + 
              #scale_x_log() +
              labs(title=col)
    # print(g.hist)
}


