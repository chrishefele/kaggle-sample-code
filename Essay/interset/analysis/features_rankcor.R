# features_rankcor.R
#
# usage:  cat features_plot.R | R --vanilla --args <infile>  

TRAINING_DATA <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
INFILE   <- commandArgs(trailingOnly=TRUE)[1] # features derived from training data

namesFilter <- function(all_names) { # return only names with specified prefixes
    all_names[c( grep("CH_",all_names), grep("BY_",all_names), grep("EJ_",all_names), 
                 grep("WC_",all_names), grep("PB_",all_names), 
                 grep("essay_id",all_names), grep("essay_set",all_names) )]
}

features <- read.csv(INFILE)
features <- features[,sort(namesFilter(names(features)))]
training <- read.delim(TRAINING_DATA, quote="")

for(eset in unique(training$essay_set)) {
    mask <- eset == training$essay_set 
    cor.method <- 'pearson' # 'spearman' for rank, 'pearson' for regular correlation
    rank.cor.df <-  as.data.frame(cor(training[mask,"domain1_score"], features[mask,], method=cor.method))
    cat(paste(cor.method, "\nCORRELATIONS for Essay set:", as.character(eset),"\n"))
    df <- as.data.frame(t(as.matrix(rank.cor.df)))
    print(df)
    df$feature_name <- row.names(df)

    #print(paste("SORTED", cor.method, "\nCORRELATIONS for Essay set:", as.character(eset)))
    #df2 <- df[order(df$V1,decreasing=TRUE),]
    #print(df2)

}



