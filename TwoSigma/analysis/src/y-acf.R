
source("read_hdf.R")
PLOT_FILE <- "../plots/y-acf.pdf"
pdf(file=PLOT_FILE)
par(mfrow=c(3,2))

train <- read_hdf("../../download/train.h5")
train.ids <- unique(sort(train$id))

# plot by starting time + end time?

for(train.id in train.ids) {

    cat("plotting id: ", train.id, "\n")
    timestamps <- train[train.id == train$id, "timestamp"]
    y          <- train[train.id == train$id, "y"]
    y.t0       <- y[1:(length(y)-1)]
    y.t1       <- y[2:(length(y)  )]

    y.bounds <- c(-0.12, 0.12)

    if(length(y) < 3) {
        cat("***** skipping id: ", train.id," with ", length(y), " points\n")
        next
    }

    scatter.smooth(timestamps, y,    
                    pch=".", 
                    lpars=list(col="red"),  
                    xlim=c(0,2000), 
                    ylim=y.bounds,
                    main=paste("id:", train.id))
    abline(h=0, col="blue")

    scatter.smooth(timestamps, y,    
                    pch=".", 
                    lpars=list(col="red"),  
                    xlim=c(0,2000), 
                    ylim=y.bounds/10,
                    main=paste("id:", train.id))
    abline(h=0, col="blue")



    # plot(timestamps, cumsum(y), type="l", main=paste("cumsum id:", train.id), xlim=c(0,2000))

    acf(y)
    hist(y, 100)

    plot(y.t0, y.t1, type="p", pch=".", xlim=y.bounds, ylim=y.bounds)
    abline(lm(y.t1 ~ y.t0), col="red")

    scatter.smooth(y.t0,       y.t1, pch=".", lpars=list(col="blue"), xlim=y.bounds,  ylim=y.bounds )

}


