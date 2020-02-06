


ones <- function(pattern, fill.value, fname) {
    template <- readRDS("../data/sample_submission.RData")
    pattern.mask <- grepl(pattern, template$Id, fixed=TRUE)
    template[pattern.mask,"Predicted"] <- fill.value
    write.csv(template, file=fname, row.names=FALSE, quote=FALSE)
    return(template)
}

ones("_62", 1, "ones-62.csv")
ones("_61", 1, "ones-61.csv")




for(pred.col in c(12, 23, 34, 47, 55, 56, 57, 58, 59, 60)) {
    grep.tag <- paste("_", pred.col, sep="")
    fname    <- paste("ones-", pred.col, ".csv", sep="")
    cat("writing: ", fname, "\n")
    ones(grep.tag, 1, fname)
}

template <- readRDS("../data/sample_submission.RData")
template$Predicted <- 1
write.csv(template, file="ones-all.csv", row.names=FALSE, quote=FALSE)


template$Predicted <- 1
pattern.mask <- grepl("_62", template$Id, fixed=TRUE) | 
                grepl("_61", template$Id, fixed=TRUE)
template[pattern.mask,"Predicted"] <- 0
write.csv(template, file="ones-intraday.csv", row.names=FALSE, quote=FALSE)

