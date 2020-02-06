# intersetFeatures.R
#
# Creates a random forest model that is applied to feature sets 
# other than the feature set the model was trained on.
#
# usage:  cat intersetFeatures.R | R --vanilla --args <feature_file_directory>  <outfile_directory>
#

library('randomForest')

TRAINING_FILE   <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
VALID_FILE      <- "/home/chefele/Essay/download/release_3/valid_set.tsv"
#FEATURES_DIR    <- commandArgs( trailingOnly=TRUE )[1] # features derived from training data
#OUTFILE_DIR     <- commandArgs( trailingOnly=TRUE )[2] # directory for output feature file

TEAM_INITIALS   <- c("CH_", "BY_", "EJ_", "WC_", "PB_")
#TEAM_INITIALS   <- c("CH_")

# random forest parameters
NTREE           <- 50  # TODO :  **** CHANGE THIS TO 500
TREE_NODE_SIZE  <- 20
RND_SEED        <- 12345678
set.seed(RND_SEED)


readTrainingFile <- function() {
    tf  <- read.delim(TRAINING_FILE, quote="")
    df <- data.frame(essay_id=tf$essay_id, essay_set=tf$essay_set, score=tf$domain1_score)
    return(df)
}

readValidationFile <- function() {
    tf  <- read.delim(VALID_FILE, quote="")
    df <- data.frame(essay_id=tf$essay_id, essay_set=tf$essay_set)
    return(df)
}

# include (or exclude) only names that have specified tags
nameFilter <- function(all_names, tags, exclude=FALSE) { 
    mask <- rep(FALSE, length(all_names))
    for(tag in tags) { 
        mask <- mask | grepl(tag, all_names)
    }
    mask <- xor(exclude, mask)
    return( all_names[mask] ) 
}

readFeatureFiles <- function(feature_dir, file_tag, eidset) {
    cat(paste("\nReading files in directory:",feature_dir,"\n"))
    # NOTE: eidset is a dataframe with at least essay_id and essay_set 
    fnames <- nameFilter( sort(dir(feature_dir)), file_tag ) # file_tags = testing, train, valid
    fnames <- nameFilter( fnames, TEAM_INITIALS )  # features starting with team member initials
    fnames <- nameFilter( fnames, 'interset', exclude=TRUE )  # CRITICAL to avoid recursive inclusions...
    features_all <- data.frame(essay_id=eidset$essay_id, essay_set=eidset$essay_set)
    for(fname in fnames) {
        fname_full <- paste(feature_dir,'/',fname,sep='')
        cat(paste("  ",fname_full,'\n'))
        fnew <- read.csv(fname_full)
        if(sum(fnew$essay_id != features_all$essay_id) >0) {
            stop("ERROR: essay_id mismatch between feature files")
        }
        feat_names <-  nameFilter(names(fnew),TEAM_INITIALS)
        feat_names <-  nameFilter(feat_names, 'interset', exclude=TRUE)
        features_all <- cbind(features_all, fnew[,feat_names] )
    }

    cat("\nFeatures:\n")
    print(as.matrix(names(features_all)))
    cat(paste("\nFeatures:", nrow(features_all),"rows X ", ncol(features_all),"columns\n"))
    return(features_all)
}


makeModels <- function(feats, train) {
    essay_sets <- sort(unique(train$essay_set))
    # make all the rf models for all the essay sets
    rf.models <- list()
    for(model_set in essay_sets) {
        cat(paste("\nMaking model for essay set:",model_set,"\n\n"))
        essay_set_mask <- train$essay_set == model_set
        x  <- feats[essay_set_mask,]
        y  <- train[essay_set_mask, 'score']  
        rf <- randomForest(x, y, ntree=NTREE, nodesize=TREE_NODE_SIZE, importance=TRUE, do.trace=TRUE) 
        rf.models[[as.character(model_set)]] <- rf
    }
    return(rf.models)
}

makePredictions <- function(rf.models, feats, eidset) {
    # now use the RF models to make predictions across all essay sets
    cat(paste("\nMaking predictions for:", nrow(feats), "rows\n"))
    rf.preds <- data.frame()
    essay_sets <- sort(unique(eidset$essay_set))
    for(essay_set in essay_sets) {
        x  <- feats[eidset$essay_set == essay_set,]
        ypreds <- data.frame( dummy=1:nrow(x) ) # pre-size the dataframe
        for(model_set in essay_sets) {
            rf.model <- rf.models[[as.character(model_set)]]
            feature.name <- paste("CH_intersetRF", model_set, sep="")
            cat(paste("essay_set:",essay_set,"feature:", feature.name,"\n"))
            ypreds[,feature.name]  <- round(predict(rf.model, x),5)  
            if(essay_set==model_set) {
                ypreds[ ,feature.name] <-  -99 # Reason: make NO intra-set predictions, ONLY inter-set
                ypreds[1,feature.name] <-  -98 # Create a slight change so correlations not undefined
            }
        }
        ypreds$dummy <- NULL
        rf.preds <- rbind(rf.preds, ypreds)
    }
    return( rf.preds ) 
}

main <- function() {
    cat("\nCreating intersetFeatures...\n\n")

    train <- readTrainingFile()   # returns dataframe with essay_id, essay_set, score 
    valid <- readValidationFile() # returns dataframe with essay_id, essay_set 

    feats_train <- readFeatureFiles(FEATURES_DIR, 'training', train)
    feats_valid <- readFeatureFiles(FEATURES_DIR, 'valid',    valid)
    if( sum(names(feats_train)!=names(feats_valid)) >0) { 
        stop("ERROR: training and valid features differ!") 
    }

    models <- makeModels(feats_train, train)

    preds_train <- makePredictions(models, feats_train, train)
    preds_valid <- makePredictions(models, feats_valid, valid)

    # add essay_id and essay_set columns back in
    train_out <- cbind(train, preds_train)
    train_out$score <- NULL
    valid_out <- cbind(valid, preds_valid)

    train_out_fname <- paste(OUTFILE_DIR, "/", "CH_intersetFeatures.training.csv",sep="")
    valid_out_fname <- paste(OUTFILE_DIR, "/", "CH_intersetFeatures.valid.csv",   sep="")
    
    cat(paste("\nWriting to:",train_out_fname),"\n")
    write.csv(train_out, file=train_out_fname, row.names=FALSE, quote=FALSE)
    cat(paste("\nWriting to:",valid_out_fname),"\n")
    write.csv(valid_out, file=valid_out_fname, row.names=FALSE, quote=FALSE)
    cat("\nFinished.\n\n")
}

# main()

FEATURES_DIR <- "/home/chefele/Dropbox/essay/final/features"
train <- readTrainingFile()   # returns dataframe with essay_id, essay_set, score 
feats_train  <- readFeatureFiles(FEATURES_DIR, 'training', train)
write.csv(feats_train, file="feats.csv", row.names=FALSE, quote=FALSE)

