train <- read.csv("/home/chefele/Ford/download/fordTrain.csv")

pdf(file="ccf.plots.pdf")

for(col.name in names(train)) {
    if( !(col.name %in% c("P8","V7","V9")) ) {
        print(col.name)
        ccf(train$IsAlert, train[[col.name]],type="correlation",lag.max=150)
        title(main=col.name)
    }
}

