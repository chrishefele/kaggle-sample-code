train <- read.csv("../download/trainTESTING.csv")

for(name in names(train)) {
    uniqs <- unique(train[,name])
    if(length(uniqs) < 100) {
        cat(name, sort(uniqs),"\n")
    }
}

