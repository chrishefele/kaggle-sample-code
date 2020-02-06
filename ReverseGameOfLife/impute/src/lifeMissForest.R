library(missForest)

TRAIN_FILE <- "syntheticTraining.csv"

BOARD_SIDE  <- 20
BOARD_CELLS <- BOARD_SIDE * BOARD_SIDE
startCols <- paste("start.",1:BOARD_CELLS, sep="")
stopCols  <- paste("stop.", 1:BOARD_CELLS, sep="")

delta <- 1

train <- read.csv(TRAIN_FILE)
cat("read:", nrow(train), " rows from ", TRAIN_FILE,"\n")

train <- train[train$delta==delta,]
cat("for subset delta=", delta, " there are ", nrow(train), " rows\n")

train.nrows <- nrow(train)
train.id <- train$id
train$id <- NULL
train.delta <- train$delta
train$delta  <- NULL

col_names <- names(train)
train[,col_names] <- lapply(train[,col_names] , factor)

train.NA <- train
train.NA[1:(train.nrows/2), startCols] <- NA  # TODO only for testing with sythetic data; update rows for real data

train.imp <- missForest(train.NA, xtrue=train, verbose=TRUE)

#print(r.imp$ximp)
#print(warnings()) # warns 5 or fewer unique values; are you sure you want regression? 
