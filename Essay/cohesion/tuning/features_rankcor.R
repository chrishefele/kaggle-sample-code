# features_rankcor.R
#
# usage:  cat features_plot.R | R --vanilla --args <infile>  

TRAINING_DATA <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
INFILE   <- commandArgs(trailingOnly=TRUE)[1] # features derived from training data

namesFilter <- function(all_names) { # return only names with specified prefixes
    all_names[c( grep("CH_",all_names), grep("BY_",all_names), grep("EJ_",all_names), 
                 grep("WC_",all_names), grep("PB_",all_names), grep("essay_set",all_names) )]
}

features <- read.csv(INFILE)
features <- features[,sort(namesFilter(names(features)))]
training <- read.delim(TRAINING_DATA, quote="")

for(eset in unique(training$essay_set)) {
    mask <- eset == training$essay_set 
    rank.cor.df <- as.data.frame(cor(training[mask,"domain1_score"], features[mask,], method="spearman"))
    print(paste("\nRANK_CORRELATIONS for Essay set:", as.character(eset)))
    print(rank.cor.df)
}



