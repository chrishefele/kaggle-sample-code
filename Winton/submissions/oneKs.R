
oneK <- function(pattern, fill.value, fname) {
    template <- readRDS("../data/sample_submission.RData")
    pattern.mask <- grepl(pattern, template$Id, fixed=TRUE)
    template[pattern.mask,"Predicted"] <- fill.value
    write.csv(template, file=fname, row.names=FALSE, quote=FALSE)
    return(template)
}


stock.Ids <- sort(sample(10000:60000, 5))

for(s in stock.Ids) {
    grep.tag <- paste(s,"_", sep="")
    fname    <- paste("oneKs-", s, ".csv", sep="")
    cat("writing: ", fname, "\n")
    oneK(grep.tag, 1000, fname)
}

