
cat('reading train\n')
train.secs <- read.csv('../features/leakage_features_train.csv')$daysec
cat('reading train truth\n')
train.truth <- read.csv('~/kaggle/WhaleRedux2/nmkridler/data/train.csv')$label

# png(filename='diff-secs-labels.png')

cap <- function(s) { 
    s[s< 0] <-  0
    s[s>50] <- 50
    return(s)
}

train.dsecs  <- cap(diff(train.secs))
train.truth <- train.truth[2:length(train.truth)]

dtrain<- table(train.dsecs, train.truth)
print(dtrain)

pct.train <- dtrain / sum(dtrain)
print(pct.train)

