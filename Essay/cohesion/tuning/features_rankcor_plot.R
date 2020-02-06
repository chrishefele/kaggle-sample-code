# features_rankcor_plot.R
#
# usage:  cat features_rankcor_plot.R | R --vanilla --args <infile>  

TRAINING_DATA <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
INFILE   <- commandArgs(trailingOnly=TRUE)[1] # features derived from training data
pdf(file='features_rankcor_plot.pdf')
par(mfrow=c(3,3)) 

features <- read.csv(INFILE)
features <- features[,sort(names(features))]
training <- read.delim(TRAINING_DATA, quote="")

for(prefix in c('CH_cohesionAdjAllRatio','CH_cohesionAdjacent','CH_cohesionAll')) {
    for(eset in unique(training$essay_set)) {
        mask <- eset == training$essay_set 
        rank.cor.df <- as.data.frame(cor(training[mask,"domain1_score"], features[mask,], method="spearman"))
        col.mask <- grepl(prefix, names(rank.cor.df))
        col.names <- names(rank.cor.df)[col.mask]

        print(paste("essay_set:", as.character(eset), prefix))
        print(rank.cor.df[,col.names])
        barplot(as.matrix(rank.cor.df[,col.names]), ylim=c(-0.5,0.5), xlab=paste(prefix), main=paste("essay_set:",as.character(eset)))
    }
    barplot(as.matrix(rank.cor.df[,col.names]), ylim=c(-0.5,0.5), xlab=paste(prefix), main=paste("essay_set:",as.character(eset)))
}



