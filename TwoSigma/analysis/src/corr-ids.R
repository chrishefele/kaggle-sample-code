
source("read_hdf.R")

PLOT_FILE <- "../plots/corr-ids.pdf"
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

y.sum <- rowSums(df)
plot(y.sum, type="l", main="sum(y)",  xlim=c(0,2000))
acf(y.sum)

hist(as.matrix(cor(df))   , 200)
hist(as.matrix(cor(noise)), 200)

cat("prcomp of y")
prc <- princomp(df, retx=TRUE)
print(summary(prc))
plot(prc)


cor.m <- as.matrix(cor(df))

cat("max    cor: ", max(cor.m),    " min  cor: ", min(cor.m),  "\n")
cat("median cor: ", median(cor.m), " mean cor: ", mean(cor.m), "\n")

cat("max    y: ", max(df),    " min  y: ", min(df),  "\n")
cat("median y: ", median(as.matrix(df)), " mean y: ", mean(as.matrix(df)), "\n")


