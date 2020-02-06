TRAIN_FILE <- "~/Supermarket/analysis/data/training.csv"

my.mode <- function(x) { names(sort(-table(x)))[1] }  # returns most frequent value

train <- read.csv(TRAIN_FILE)
train$visit_weekday <- format(as.Date(train$visit_date),"%w")
train$gaps <- c( diff(as.Date(train$visit_date)), 0) # days between shopping visits 
mask <- (train$gaps>=0) & (train$gaps<15) & (train$visit_spend<200)
train <- train[mask,] 

hist(train$visit_spend, 40)

hist(train$gaps, 15) 

plot(table(train$visit_weekday),type="b")

acf(train$visit_spend)

acf(train$gaps) 

plot(tapply(train$visit_spend, train$gaps, mean))

plot(tapply(train$visit_spend, train$gaps, median))

plot(tapply(train$gaps, as.integer(train$visit_spend), mean), type="b")

plot(tapply(train$gaps, as.integer(train$visit_spend), my.mode), type="b")

# given weekday, spend, current inventory, last gap --> next gap   -> spend on that day 
# given weekday, spend, current inventory, last gap --> next spend -> next gap 

