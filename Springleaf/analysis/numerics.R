train <- read.csv("../download/train.csv", stringsAsFactors=FALSE)

for(name in names(train)) {
    x <- train[,name]
    if(is.numeric(x)) {
        cat(name, "\n")
        print(table(x))
        cat("------------------------------------------------------------------------------\n")
    } 
}


