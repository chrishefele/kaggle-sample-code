
source("read_hdf.R")

PLOT_FILE <- "../plots/corr-ids-lead-lag.pdf"
pdf(file=PLOT_FILE)

train <- read_hdf("../../download/train.h5")
train.ids <- unique(sort(train$id))

df    <- data.frame(dummy=numeric(1813))
noise <- data.frame(dummy=numeric(1813))

for(train.id in train.ids) {

    cat("processing id: ", train.id)

    timestamps <- train[train.id == train$id, "timestamp"]
    y          <- train[train.id == train$id, "y"]
    id.name    <- paste("id_", train.id, sep="")

    if(length(y) != 1813) {
        cat("  skipping; length is: ", length(y), "\n")
        next
    } else {    
        cat("\n")
    }

    df[,id.name] <- y[order(timestamps)]
    #noise[,id.name] <- rnorm(length(y))
    noise[ ,id.name] <- sample(df[,id.name])

    #plot(timestamps, y, type="l", main=paste("id:", train.id), xlim=c(0,2000))

}

df$dummy <- NULL


df.t0  <- df[1:(length(df)-1),]
df.t1  <- df[2:(length(df)  ),]

noise.t0  <- noise[1:(length(df)-1),]
noise.t1  <- noise[2:(length(df)  ),]

hist.cor <- function(df0, df1) {

    m <- as.matrix(cor(x=df0, y=df1))
    m[abs(m)>0.99] <- NA

    l <- 0.2
    # hist(m, 200, prob=TRUE, xlim=c(-l,l), ylim=c(0,5000))
    hist(m, 200, prob=TRUE, xlim=c(-l,l))
    abline(v=median(m, na.rm=TRUE), col = "red", lwd = 2)
    lines(density(m, na.rm=TRUE), col="blue")
}

hist.cor(df.t1,      df.t0)
hist.cor(df.t1,     -df.t0)
hist.cor(noise.t1,  noise.t0)
hist.cor(noise.t1, -noise.t0)
