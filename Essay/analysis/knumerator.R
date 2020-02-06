
TRAIN <- "/home/chefele/Essay/download/release_2/training_set_rel2.tsv"

train <- read.delim(TRAIN)

train <- train[train$essay_set==1,]

r1 <- train$rater1_domain1
r2 <- train$rater2_domain1

table(r1)
table(r2)
table(r1,r2)

agree <- as.matrix(table(r1,r2))
print(agree)

rg <- min(r1,r2):max(r1,r2)
print(rg)


m<-as.matrix(rep(rg, length(rg)))
dim(m) <- c(length(rg),length(rg))
sqerrs <- (m-t(m))^2
print(sqerrs)

print(agree*sqerrs)

#contour plot

contour(agree*sqerrs)



