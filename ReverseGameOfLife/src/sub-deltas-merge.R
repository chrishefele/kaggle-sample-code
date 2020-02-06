# R script to create the final submission from
# submissions created for each delta seperately 

getSubmission <- function(filename) {
    cat("reading: ",filename,"\n")
    read.csv(filename)
}

ids <- getSubmission("sub-deltas-10000.csv")$id

merged.sub <-   getSubmission("sub-deltas-10000.csv") + 
                getSubmission("sub-deltas-02000.csv") + 
                getSubmission("sub-deltas-00300.csv") + 
                getSubmission("sub-deltas-00040.csv") + 
                getSubmission("sub-deltas-00005.csv") 

merged.sub$id <- ids # overwrite, since original ids get summed above

SUBMISSION_MERGED <- "sub-deltas-12345.csv"
cat("writing submission: ",SUBMISSION_MERGED ,"\n")
write.csv(merged.sub, file=SUBMISSION_MERGED, quote=FALSE, row.names=FALSE, col.names=TRUE)



