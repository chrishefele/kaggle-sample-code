
pdf(file="plot-ret-sorted.pdf")

train <- readRDS("../data/train.RData")

rp2 <- train$Ret_PlusTwo

y <- sort(rp2)

for(width in c(19000, 8000, 4000, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1)) {
    ctr <- 20000
    ix  <- c( (ctr-width):(ctr+width) )
    cat("plotting width:", width, "\n")
    plot(ix, y[ix], type="l")
}


