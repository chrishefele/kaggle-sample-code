# noisify.R
#
# Adds noise to ratings to see if this helps improve scores by equilizing histograms
#
# usage:  cat noisify.R | R --vanilla 

library('irr')      # for kappa statistic calculation
library('glmnet') 

TRAINING_FILE <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
#FEATURES_FILE <- "/home/chefele/Essay/xfeatures/results/xfeatures.training.csv"
FEATURES_FILE <- "/home/chefele/Essay/noisify/data/all_features_reduced.csv"

# --------------- utility functions

noisyScores <- function(scores, noise.mag) { 
   #z <- scores + noise.mag*(runif(length(scores))-0.5) # add noise; use rnorm?
    z <- scores + noise.mag*(rnorm(length(scores))) # add noise
    z <- round(z)            # dumb rounding 
    z <- pmin(z,max(scores)) # don't go past highest score
    z <- pmax(z,min(scores)) # don't go past lowest  score
    return(z)
}


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

# ---------- now fit & compare models using original scores & noisified scores

for(nz.lvl in c(0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0)) {
    for(iter in 1:10) { 
        print(paste("Iteration:", as.character(iter)))
        print("Fitting the models")
        tenfold_ids <- 1:nrow(xm) %% 10 + 1  # use same CV folds for both fits below
        fit.nonoise <- cv.glmnet(xm, y,                      family="gaussian", foldid=tenfold_ids)
        fit.noise   <- cv.glmnet(xm, noisyScores(y, nz.lvl), family="gaussian", foldid=tenfold_ids)

        ypred.nonoise <- round(predict(fit.nonoise, xm, type="response"))
        ypred.noise   <- round(predict(fit.noise,   xm, type="response"))

        kappa.nonoise <- kappa2( data.frame(y, ypred.nonoise[,1]), weight="squared")
        kappa.noise   <- kappa2( data.frame(y, ypred.noise[,1]  ), weight="squared")

        kno <- as.character(kappa.nonoise$value)
        knz <- as.character(kappa.noise$value  )
        nzl <- as.character(nz.lvl)

        print(paste("RESULT", "KappaUnNoised=",kno,"KappaNoised=", knz, "NoiseLevel=",nzl))
    }
}


#head(y, 20)
#head(noisyScores(y,0.0),20)
#head(noisyScores(y,2.0),20)
#head(ypred.nonoise[,1], 20)
#head(ypred.noise[,1],   20)

