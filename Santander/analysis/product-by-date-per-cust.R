
library(readr)
library(corrplot)


N_SAMPLES  <- 300000
TRAIN_CSV <- "../data/train_ver2.csv"
#TRAIN_CSV <- "../data/head-train_ver2.csv"
PLOT_PDF  <- "../plots/product-by-date-per-cust.pdf"

make.plot <- function(df.in) {
    if(nrow(df.in) <2) {
        cat(" tooFewRows\n")
        return()
    }
    df <- as.data.frame(df.in[,c(1,2,25:48)])
    cust <- unique(df$ncodpers)[1]
    cat("ncodpers: ", cust)

    df <- df[order(df$fecha_dato),]
    row.names(df) <- df$fecha_dato # date
    df$fecha_dato <- NULL
    df$ncodpers   <- NULL
    M <- data.matrix(df)
    if(any(is.na(M))) { 
        cat(" skippedDueToNA\n")
        return()
    }
    if(sum(M, na.rm=TRUE)==0) {
        cat(" noProducts\n")
        return()
    }
    if( nrow(M)>1 && all(M[nrow(M),] <= M[nrow(M)-1,]) ) {
        cat(" noNewProducts\n")
        return()
    }

    added.products <- M[nrow(M),] > M[nrow(M)-1,]
    M[nrow(M),  ]  <- M[nrow(M),  ] * (1-2*added.products)
    corrplot(M, method="circle", is.corr=FALSE, type="full", 
             title=paste("ncodpers:", cust), cl.pos="n", tl.cex=0.8, mar=c(0,0,2,0))
    cat(" plotted\n")
    return()
}

pdf(file=PLOT_PDF)

cat("reading: ", TRAIN_CSV, "\n")
train <- read_csv(TRAIN_CSV, progress=TRUE)

cat("sampling ", N_SAMPLES, " ncodpers from training set\n")
sampled.ncodpers <- sample(unique(train$ncodpers), N_SAMPLES)
train <- train[train$ncodpers %in% sampled.ncodpers,]
cat("done sampling\n")

suppressed.output <- by(train, factor(train$ncodpers), make.plot)

cat("wrote plots to:", PLOT_PDF, "\n")

