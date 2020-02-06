
pdf(file="optimal-scale-sumabs-to-dailyret.pdf")

library("quantreg")

train <- readRDS("../../data/train.RData")
train[is.na(train)] <- 0

# ----------------- global scale optimization

rp2 <- train$Ret_PlusTwo
rp1 <- train$Ret_PlusOne
rm1 <- train$Ret_MinusOne
rm2 <- train$Ret_MinusTwo 

returns             <- train[, paste("Ret_", c(2:120), sep="")]
returns.sumabs      <- apply(returns, 1, function(x) sum(   abs(x)))

print( rq(abs(rp2) ~ 0 + returns.sumabs) )
print( rq(abs(rp1) ~ 0 + returns.sumabs) )
print( rq(abs(rm1) ~ 0 + returns.sumabs) )
print( rq(abs(rm2) ~ 0 + returns.sumabs) )

# ----------------- scale optimization per group

best.scales <- c()
best.scale.signedrets <- c()
cors.medians<- c()
score.impacts <- c()

groups <- sort(unique(train$Feature_7))

for(group in groups) {

    row.select  <- train$Feature_7 == group
    col.select  <- paste("Ret_", c(2:120), sep="") 
    returns     <- train[row.select, col.select ] 
    returns.sumabs <- apply(returns, 1, function(x) sum(   abs(x)))

    rp2 <- train[ row.select, "Ret_PlusTwo" ]

    model <- rq( abs(rp2) ~ 0 + returns.sumabs ) 
    best.scale <- coef(model)[["returns.sumabs"]]
    
    model <- rq( rp2 ~ 0 + returns.sumabs ) 
    best.scale.signedret <- abs(coef(model)[["returns.sumabs"]])

    # use rank correlation to reduce the impact of noise/outliers
    cors.median <- median(c(cor(t(returns), method="spearman"))) 

    score.impact <- sum(returns.sumabs) * 0.18 * sqrt(cors.median)

    s <- sprintf("group %8i best.scale %7.4f best.scale.signedret %7.4f cors.median %7.4f score.impact %7.4f", 
                    group, best.scale, best.scale.signedret, cors.median, score.impact)
    cat(s, "\n")

    best.scales             <- c(best.scales,  best.scale)
    best.scale.signedrets   <- c(best.scale.signedrets,  best.scale.signedret)
    cors.medians            <- c(cors.medians, cors.median)
    score.impacts           <- c(score.impacts, score.impact)

}

cat("Group info sorted by score.impact\n")
group.info <- data.frame(   groups, 
                            best.scales, best.scale.signedrets, 
                            cors.medians, score.impacts )
print(head(group.info[order(group.info$score.impact, decreasing=TRUE),], 20))
print(head(group.info[order(group.info$cors.medians, decreasing=TRUE),], 20))

hist(score.impacts, 50)
hist(log10(score.impacts), 50)
plot(sort(score.impacts, decreasing=TRUE), type="b")
plot(sort(score.impacts, decreasing=TRUE), type="b", log="x")

hist(best.scales)
hist(best.scales, 40)
hist(log10(best.scales))
hist(log10(best.scales), 40)

plot(sort(best.scales), type="l")
plot(sort(best.scales), type="l", log="x")
plot(sort(best.scales), type="l", log="y")
plot(sort(best.scales), type="l", log="xy")

plot(cors.medians, best.scale.signedrets, xlab="cors.median", ylab="best.scale")
lines(lowess(cors.medians, best.scale.signedrets, f=1./5), col="blue")

plot(cors.medians, best.scale.signedrets/0.18, xlab="cors.median", ylab="best.scale/0.18")
lines(lowess(cors.medians, best.scale.signedrets/0.18, f=1./5), col="blue")
lines(cors.medians, sqrt(cors.medians), col="green")

plot(cors.medians, best.scale.signedrets, xlab="cors.median", ylab="best.scale", log="x")
lines(lowess(cors.medians, best.scale.signedrets, f=1./5), col="blue")

plot(cors.medians, best.scale.signedrets, xlab="cors.median", ylab="best.scale", log="y")
lines(lowess(cors.medians, best.scale.signedrets, f=1./5), col="blue")

plot(cors.medians, best.scale.signedrets, xlab="cors.median", ylab="best.scale", log="xy")
lines(lowess(cors.medians, best.scale.signedrets, f=1./5), col="blue")

