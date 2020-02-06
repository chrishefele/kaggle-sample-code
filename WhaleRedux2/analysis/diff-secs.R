

cat('reading test\n')
test.secs  <- read.csv('../features/leakage_features_test.csv')$daysec
cat('reading train\n')
train.secs <- read.csv('../features/leakage_features_train.csv')$daysec

png(filename='diff-secs.png')

cap <- function(s) { 
    s[s< 0] <-  0
    s[s>50] <- 50
    return(s)
}

test.dsecs  <- cap(diff(test.secs))
train.dsecs <- cap(diff(train.secs))

print(table(test.dsecs))
print(table(train.dsecs))

pct.test  <- table(test.dsecs) / sum( table(test.dsecs) ) 
pct.train <- table(train.dsecs)/ sum( table(train.dsecs) ) 

print(pct.test)
print(pct.train)

print(median(test.dsecs))
print(median(train.dsecs))
print(mean(test.dsecs))
print(mean(train.dsecs))

plot(   pct.test, 
        type='s', ylim=c(-0.2,0.2),
        main='Distribution of delta seconds',
        xlab='delta (secs)',
        ylab='fraction',
        col='red'
)
lines(-pct.train, type='s', ylim=c(-0.2,0.2), col='blue')
lines(-pct.test , type='p', ylim=c(-0.2,0.2), col='red')
lines( pct.train, type='p', ylim=c(-0.2,0.2), col='blue')

legend("topleft", c('test','train'),
        cex=0.8, col=c('red','blue'),
        lty=1:3, lwd=2,bty='n'
)


