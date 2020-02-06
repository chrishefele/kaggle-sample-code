
source("read_hdf.R")
PLOT_FILE <- "../plots/y-vs-timestamp.pdf"
pdf(file=PLOT_FILE)

train <- read_hdf("../../download/train.h5")
train.ids <- unique(sort(train$id))


# plot by starting time + end time?

for(train.id in train.ids) {

    cat("plotting id: ", train.id, "\n")
    timestamps <- train[train.id == train$id, "timestamp"]
    y          <- train[train.id == train$id, "y"]
    plot(timestamps, y, type="l", main=paste("id:", train.id), xlim=c(0,2000))

}

