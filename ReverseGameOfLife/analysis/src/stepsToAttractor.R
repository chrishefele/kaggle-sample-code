boardData <-read.csv('stepsToAttractor.csv')
pdf(file='stepsToAttractor.pdf')


for(side in unique(boardData$side)) {
    steps <- boardData[boardData$side==side,]$steps
    cat("side_length:", side, "median_steps:", median(steps), "mean_steps:", mean(steps))
    cat('  sqrt_steps/side_len:', mean(sqrt(steps))/side)
    cat(' steps/cell:', mean(steps)/(side*side),'\n')
    hist(steps, 100)
    hist(log10(steps), 100, main='log10 steps')
    hist(c(1,steps[steps>5]), breaks=100, main='steps after burn-in')
}
geomean <- function(x) {exp(mean(log(x)))}
plot( tapply(     boardData$steps, boardData$side, mean))
plot( tapply(sqrt(boardData$steps), boardData$side, mean) )
plot( tapply(sqrt(boardData$steps), boardData$side, geomean) )
boxplot(sqrt(steps)~side, data=boardData, outline=FALSE, ylim=c(0,10))

steps20 <- boardData[boardData$side==20,]$steps
print(table(steps20))
plot(table(steps20))

steps20gt5 <- steps20[steps20>5]
print(mean(  steps20gt5))
print(median(steps20gt5))

