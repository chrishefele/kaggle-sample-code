# usage:  cat reduced_stats.R | R --vanilla 

namesFilter <- function(all_names) { # return only names with specified prefixes
    all_names[c( grep("CH_",all_names), grep("BY_",all_names), grep("EJ_",all_names), 
                 grep("WC_",all_names), grep("PB_",all_names) )]
}

DATA_DIR = "../data2/"
for(fname in list.files(path=DATA_DIR)) {
    infile <- paste(DATA_DIR,fname,sep="")
    all.dat <- read.csv(infile)
    train.mask <- all.dat$sett == 1
    features <- all.dat[train.mask, sort(namesFilter(names(all.dat)))]
    target   <- all.dat[train.mask, "target"]
    cors <- cor(target, features, method="spearman")
    cors.print <- as.data.frame(t(as.matrix(as.data.frame(cors))))
    print(paste("CORRELATIONS:", fname))
    print(cors.print)
    
    msg <- "MEDIAN feature-feature correlation:" 
    outstring <- paste(msg, as.character(median(cor(features, features,method="spearman"))))
    print(outstring)
    print(ncol(features))

    hist(cor(features, features, method="spearman"), breaks=100, main=fname, xlim=c(-1,1))
}


