train <- read.csv("../download/train.csv")
pdf(file="hists.pdf")

for(name in names(train)) {
    cat(name,"\n")
    x <- train[,name]
    if(is.numeric(x)) {
        hist(x, 500, main=name)
    } else {
        cat(name, "is non-numeric\n")
    }
}


