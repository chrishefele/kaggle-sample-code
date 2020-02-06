# features_plot.R
#
# Makes boxplots and histograms of features generated from training data
#
# usage:  cat features_plot.R | R --vanilla --args <infile>  <plotfile>

TRAINING_DATA <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"

INFILE   <- commandArgs(trailingOnly=TRUE)[1] # features derived from training data
PLOTFILE <- commandArgs(trailingOnly=TRUE)[2] # .PDF output filename for plots

features <- read.csv(INFILE)
training <- read.delim(TRAINING_DATA, quote="")
features$domain1_score <- training$domain1_score

pdf(file=PLOTFILE)
par(mfrow=c(3,3))  # set 2 by 2 plots per page

# make boxplots of scores vs feature values, one per essay set
for(feat in sort(names(features))) {
    for(eset in unique(features$essay_set)) {
        fdat <- features[features$essay_set == eset,]
        plot_title <- paste(feat,"set", as.character(eset),"")
        # plot( fdat[[feat]], fdat[["domain1_score"]], main=plot_title, xlab=feat, ylab="Domain 1 Score")
        boxplot( tapply( fdat[[feat]], fdat[["domain1_score"]], c ), 
                 main=plot_title, xlab=feat, ylab="Domain 1 Score", horizontal=TRUE )
    }
    plot(c(0,0,1,1,0,0,1), c(0,1,1,0,0,1,0), type="l", xlab="", ylab="", main="")
}

# make histograms of feature values, one per essay set
for(feat in sort(names(features))) {
    for(eset in unique(features$essay_set)) {
        fdat <- features[features$essay_set == eset,]
        plot_title <- paste(feat, "set", as.character(eset),"")
        hist(fdat[[feat]], 100, main=plot_title, xlab=feat, ylab="Hits")
    }
    plot(c(0,0,1,1,0,0,1), c(0,1,1,0,0,1,0), type="l", xlab="", ylab="", main="")
}


