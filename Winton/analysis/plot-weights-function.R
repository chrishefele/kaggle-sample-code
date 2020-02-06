library(ggplot2)

WEIGHTS.PLOT.FILE <- "plot-weights-function.pdf"

pdf(file=WEIGHTS.PLOT.FILE)

gplot.xy <- function(x, y, title, x.name, y.name) {
    jit.scale <- 0.1 # jitter scaling factor
    df.xy <- data.frame(
                        x=jitter(x, factor=jit.scale), 
                        y=jitter(y, factor=jit.scale) 
                       )
    ggraph <-   ggplot(df.xy, aes(x=x,y=y)) + 
                geom_point(alpha=0.2) + 
                ggtitle(title) + 
                labs(x=x.name, y=y.name) + 
                geom_smooth(method="loess", size=2) + 
                stat_quantile(quantiles=c(0.5), formula=y~x, colour = "red", size=2)
    print(ggraph)
}

main <- function() {

    train   <- readRDS("../data/train.RData")
    wts     <- train[,"Weight_Intraday"]


    if(TRUE) {
        ix <- sample(1:length(wts), 4000)
        wts     <- wts[ix]
        train   <- train[ix,]
    }

    for(col in names(train)) {
        if(col=="Id") next
        cat("plotting: ", col,"\n")
        if(grepl("Ret_", col, fixed=TRUE)) {
            xplot <- log10(abs(train[,col]) + 1E-6)
        } else {
            xplot <- train[,col]
        }
        gplot.xy(xplot, wts, col, col, "weight")

    }

}

main()

