
# plot histograms of non-binary variables in dataset 

DATA_DIR = "col_vals.allmin.uniques"
pdf("col_vals_allmin_hists.pdf")
for(f in dir(path=DATA_DIR)) {
    print(f)
    df <- read.csv(paste(DATA_DIR,f,sep="/"),header=FALSE)

    vals <- df$V1
    vals[vals>1] <- 1 # clamp to 1 on upper end
    vals[vals<0] <- 0 # clamp to 0 on lower end
    vals <- c(0,vals) # add one zero to set range

    n_unique <- length(unique(vals))
    if(n_unique>2) {
        uniques_msg <- paste(" UniqueVals:",as.character(n_unique))
        hist(vals, main=paste("(Max1) Histogram of:", f, uniques_msg), 100)
    }

}


