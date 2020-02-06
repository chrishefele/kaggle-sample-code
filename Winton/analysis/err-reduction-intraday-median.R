
RETURNS.FILE  <- "../data/train.RData"

row.median.abs <- function(df) { apply(abs(df), 1, median) }
row.median     <- function(df) { apply(    df,  1, median) }

train <- readRDS(RETURNS.FILE)
train[is.na(train)] <- 0
rownames(train) <- train$Id

H3.COLS <- paste("Ret_", 121:180, sep="")
preds.median.abs <- row.median.abs(train[, H3.COLS])
preds.median     <- row.median(    train[, H3.COLS])
preds.zero       <- 0 * preds.median.abs 

returns <- train[, H3.COLS]

err.pos <- rowSums( abs(returns -  preds.median.abs) )
err.neg <- rowSums( abs(returns - -preds.median.abs) )
errs.median.abs <- pmin(err.pos, err.neg)

errs.median     <- rowSums( abs(returns - preds.median ) )

errs.zero       <- rowSums( abs(returns - 0 ) )

print(sum(errs.median))
print(sum(errs.median.abs))
print(sum(errs.zero))

print(sum(err.pos))
print(sum(err.neg))
print(sum(pmin(err.pos, err.neg)))
print(sum(pmax(err.pos, err.neg)))

