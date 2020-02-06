library(missForest)

ROWS <- 2000
COLS <- 50

vals <- c(1:(ROWS*COLS)) %% 2
#vals <- 1*(runif(ROWS*COLS) > 0.7)

train <- matrix(vals, nrow=ROWS, ncol=COLS )
train <- as.data.frame(train)

col_names <- names(train)
train[,col_names] <- lapply(train[,col_names] , factor)

train.NA <- train
train.NA[1:(ROWS/2), 1:(COLS/2)] <- NA

print(train)
print(summary(train))
print(train.NA)
print(summary(train.NA))

train.imp <- missForest(train.NA, xtrue=train, verbose=TRUE )

print(train.imp$ximp)

print(train.imp$ximp == train)


