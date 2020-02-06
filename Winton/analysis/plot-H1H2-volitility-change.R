
RETURNS.FILE  <- "../data/train.RData"
PLOT.FILE     <- "plot-H1H2-volitility-change.pdf"

row.median.abs <- function(df) { apply(abs(df), 1, median) }
row.mean.abs   <- function(df) { apply(abs(df), 1, mean)   }

pdf(file=PLOT.FILE)
par(mfrow=c(2,2))

train <- readRDS(RETURNS.FILE)
train[is.na(train)] <- 0
rownames(train) <- train$Id

H1.COLS <- paste("Ret_",   2: 60, sep="")
H2.COLS <- paste("Ret_",  61:120, sep="")
H3.COLS <- paste("Ret_", 121:180, sep="")
H1H2.COLS <- c(H1.COLS, H2.COLS)

df <- train[,c("Id", "Feature_7", H1H2.COLS)]

#h1.mag <- row.median.abs(train[, H1.COLS])
#h2.mag <- row.median.abs(train[, H2.COLS])

h1.mag <- row.mean.abs(train[, H1.COLS])
h2.mag <- row.mean.abs(train[, H2.COLS])

df$mag.ratio <- h1.mag / h2.mag

df <- df[order(df$mag.ratio),]

for(row.num in 1:nrow(df)) {
    stock.id <- df[row.num, "Id"]
    f7       <- df[row.num, "Feature_7"]
    rets     <- as.numeric(df[row.num, H1H2.COLS])
    ratio    <- df[row.num, "mag.ratio"]

    if(ratio > 2.0 || ratio < 0.5) {
        cat("plotting ", "stock.id: ", stock.id, " f7: ", f7, " ratio: ", ratio, "\n")
        tag <- paste("id",stock.id, "f7", f7, "ratio", ratio)
        plot(rets, main=tag, type="l")
    } else {
        cat("skipping ", "stock.id: ", stock.id, " f7: ", f7, " ratio: ", ratio, "\n")
    }

}


