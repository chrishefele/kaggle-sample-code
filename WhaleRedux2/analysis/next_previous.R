train <- read.csv('~/kaggle/WhaleRedux2/nmkridler/data/train.csv')

w <- train$label

print_bits <- function(w) {
    n <- length(w)
    bits <- paste(
                  as.character(w[1:(n-2)]),   
                  as.character(w[2:(n-1)]),
                  as.character(w[3:(n-0)]), sep='')
    print(table(bits))
    return(table(bits))
}

l <- train$label
print("original order labels")
b1 <- print_bits(l)
print("random order labels")
b2 <- print_bits(sample(l, length(l)))

print("original order / random order")
print(b1/b2)



