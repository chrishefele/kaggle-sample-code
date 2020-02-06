# set8.hists.R
#
# Set 8 histograms at various resolutions
#
# usage:  cat set8.hists.R | R --vanilla 

library('irr')      # for kappa statistic calculation
library('glmnet') 

TRAINING_FILE <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
#FEATURES_FILE <- "/home/chefele/Essay/xfeatures/results/xfeatures.training.csv"
FEATURES_FILE <- "/home/chefele/Essay/noisify/data/all_features_reduced.csv"

# --------------- utility functions

namesFilter <- function(all_names) { # return only names with specified prefixes
    all_names[c( grep("CH_",all_names), grep("BY_",all_names), grep("EJ_",all_names), 
                 grep("WC_",all_names), grep("PB_",all_names), grep("essay_set",all_names) )]
}


# ---- read in the data...

# the following is used for xfeatures.training.csv only 
# features   <- read.csv(FEATURES_FILE)  

# the following extracts features from the all_features_reduced.csv file
fin        <- read.csv(FEATURES_FILE)
features   <- fin[ fin$sett==1, namesFilter(names(fin)) ]
training   <- read.delim(TRAINING_FILE, quote="")

# --------- select data for the essay set under study

essay_set <- 8
print(paste("Using essay set:",as.character(essay_set)))
x  <- features[features$essay_set == essay_set,]
xm <- as.matrix(x)
y  <- training[training$essay_set == essay_set, 'domain1_score']

pdf(file='set8.hists.pdf')

for(rez in 5:100) {
    hist(y, rez)
}

