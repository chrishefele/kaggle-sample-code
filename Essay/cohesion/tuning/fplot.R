# fplot.R
#
# usage:  cat fplot.R | R --vanilla --args <infile>  

TRAINING_DATA <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
INFILE   <- commandArgs(trailingOnly=TRUE)[1] # features derived from training data
pdf(file='fplot.pdf')
par(mfrow=c(3,3)) 

features <- read.csv(INFILE)
features <- features[,sort(names(features))]
training <- read.delim(TRAINING_DATA, quote="")

getMiddleName <- function(nm) { strsplit(nm,"_")[[1]][2] } 
uniqMiddleNames <- paste("_",unique(sapply(names(features), getMiddleName)),sep="")
print(uniqMiddleNames)

for(middleName in uniqMiddleNames) {
    for(eset in unique(training$essay_set)) {
        mask <- eset == training$essay_set 
        rank.cor.df <- as.data.frame(cor(training[mask,"domain1_score"], features[mask,], method="spearman"))
        col.mask <- grepl(middleName, names(rank.cor.df))
        col.names <- names(rank.cor.df)[col.mask]

        print(paste("essay_set:", as.character(eset), middleName))
        print(rank.cor.df[,col.names])
        barplot(as.matrix(rank.cor.df[,col.names]), ylim=c(-1.0,1.0), xlab=paste(middleName), main=paste("essay_set:",as.character(eset)))
    }
    barplot(as.matrix(rank.cor.df[,col.names]), ylim=c(-1.0,1.0), xlab=paste(middleName), main=paste("essay_set:",as.character(eset)))
}

