
source("read_hdf.R")

train <- read_hdf("../../download/train.h5")

train.ids <- unique(sort(train$id))

for(train.id in train.ids) {

    tstamp <- train[train.id == train$id, "timestamp"]
    tstamp <- sort(tstamp)

    tstamp.len <- length(tstamp)
    tstamp.min <- min(tstamp)
    tstamp.max <- max(tstamp)

    cat("train id: ", train.id, " len: ", tstamp.len, " tmin: ", tstamp.min, " tmax: ", tstamp.max)
    cat(" diffs:", as.vector(unique(diff(tstamp))), "\n")

}

