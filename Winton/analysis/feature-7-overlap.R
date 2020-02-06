
train <- readRDS("../data/train.RData")
test  <- readRDS("../data/test.RData")

f7.test  <- unique( test$Feature_7)
f7.train <- unique(train$Feature_7)

cat("\ncommon Feature_7 values in test and train\n")
print(intersect(f7.test, f7.train))

find.twins <- function(f7.vec) {
    twins.upper <- intersect(f7.vec, f7.vec + 1)
    twins <- sort(c(twins.upper, twins.upper -1))
    return(twins)
}

cat("\ntwins in train\n")
print(find.twins(f7.train))

cat("\ntwins in test\n")
print(find.twins(f7.test))


cat("\ncross-twins in test and train\n")
print(intersect(f7.test, f7.train))
print(intersect(f7.test+1, f7.train))
print(intersect(f7.test, f7.train+1))

