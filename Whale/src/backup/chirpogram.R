
TRAIN_FEATURES <- '../features/chirp_features_train_3000.csv'
PLOT_FILE <-  'chirpogram.pdf'
LABEL_FILE <- '../download/data/train.csv'

cat('\n*** generating chirpograms ***\n')

train <- read.csv(TRAIN_FEATURES)
clip_name <- train$clip_name
train$clip_name <- NULL
labels <- read.csv(LABEL_FILE)$label

for(i in 1:nrow(train)) {

    whale_tag <- ifelse(labels[i]==1, 'whale_yes', 'whale_no') 
    plot_title <- paste(clip_name[i], whale_tag)
    cat(plot_title)
    cat('\n')

    row <- t(train[i,])
    image(matrix(row,30,30), main=plot_title)
}

