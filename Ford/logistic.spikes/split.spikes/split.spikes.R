TRAIN_FILE    <- "/home/chefele/Ford/download/fordTrain.csv"
TEST_FILE     <- "/home/chefele/Ford/download/fordTest.csv"

TRAIN_SPIKE_FILE    <- "fordTrain.spike.csv"
TRAIN_NOSPIKE_FILE  <- "fordTrain.nospike.csv"

TEST_SPIKE_FILE    <- "fordTest.spike.csv"
TEST_NOSPIKE_FILE  <- "fordTest.nospike.csv"

spikeMask <- function(df) {
    means <- tapply(df$P2, df$TrialID, mean)
    SPIKE.THRESHOLD <- 12.5
    spikeIDs <- as.integer(rownames( means[means>SPIKE.THRESHOLD] ))
    mask <- (df$TrialID %in% spikeIDs)
    return(mask)
}

train <- read.csv(TRAIN_FILE)
train.spike     <- train[ spikeMask(train) ,]
train.nospike   <- train[!spikeMask(train) ,]

test <- read.csv(TEST_FILE)
test.spike     <- test[ spikeMask(test) ,]
test.nospike   <- test[!spikeMask(test) ,]

write.csv(train.spike,   file=TRAIN_SPIKE_FILE,   row.names=FALSE,quote=FALSE)
write.csv(train.nospike, file=TRAIN_NOSPIKE_FILE, row.names=FALSE,quote=FALSE)

write.csv(test.spike,   file=TEST_SPIKE_FILE,   row.names=FALSE,quote=FALSE)
write.csv(test.nospike, file=TEST_NOSPIKE_FILE, row.names=FALSE,quote=FALSE)


