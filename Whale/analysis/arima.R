train <- read.csv('~/kaggle/Whale/download/data/train.csv')

print_arimas <- function(dat) {

for(p1 in c(0,1)) {
    for(p2 in c(0,1)) {
        for(p3 in c(0,1)) {
            print(c(p1,p2,p3))
            print(arima(dat,                      order=c(p1,p2,p3)))
            print(arima(sample(dat, length(dat)), order=c(p1,p2,p3)))
            cat('\n')
            cat('\n')
        }
    }
}
}

print_arimas(train$label)


