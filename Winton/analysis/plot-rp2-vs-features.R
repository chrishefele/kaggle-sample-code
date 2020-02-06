library(ggplot2)

WEIGHTS.PLOT.FILE <- "plot-rp2-vs-features.pdf"

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
    target  <- log10(abs(train[,"Ret_PlusTwo"]) + 1E-6)

    # use a sample for speed...
    if(TRUE) {
        ix <- sample(1:length(target), 4000)
        target <- target[ix]
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
        gplot.xy(xplot, target, col, col, "Ret_PlusTwo")

    }

}

main()

