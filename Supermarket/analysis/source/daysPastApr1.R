TRAIN_FILE <- "~/Supermarket/analysis/data/training.csv"
train <- read.csv(TRAIN_FILE)
train$day_num  <- as.Date(train$visit_date) - as.Date("2011-04-01")
apr1 <- train[train$day_num>=0,]
apr1$day_num_int <- as.integer(apr1$day_num)
per.cust.min.daynums <- tapply(apr1$day_num_int, apr1$customer_id,min)

# Conclusion: if randomly picking a day in any range after Apr1, picking a constant Apr 1 is best.
# Picking between more than 1 day (i.e. Apr 1) lessens the overall probablity of success.
for( n in 0:30 )  {
    random.predictor <- sample(0:n, length(per.cust.min.daynums), replace=T)
    random.predictor.matches <- sum(random.predictor == per.cust.min.daynums)
    print(n)
    print(random.predictor.matches)
}

counts <- table(per.cust.min.daynums)
cumsum(counts)/sum(counts)
counts/sum(counts)

pdf("daysPastApr1.pdf") 
counts.15 <- counts[1:15]
plot(counts.15/sum(counts))
plot(cumsum(counts.15)/sum(counts))



