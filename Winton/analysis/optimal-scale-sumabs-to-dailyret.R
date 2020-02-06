
pdf(file="optimal-scale-sumabs-to-dailyret.pdf")

library("quantreg")

train <- readRDS("../data/train.RData")

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
for(group in unique(train$Feature_7)) {

    row.select  <- train$Feature_7 == group
    col.select  <- paste("Ret_", c(2:120), sep="") 
    returns     <- train[row.select, col.select ] 
    returns.sumabs <- apply(returns, 1, function(x) sum(   abs(x)))

    rp2 <- train[ row.select, "Ret_PlusTwo" ]

    model <- rq( abs(rp2) ~ 0 + returns.sumabs ) 
    best.scale <- coef(model)[["returns.sumabs"]]
    cat("group: ", group, " best.scale: ", best.scale, "\n")
    best.scales <- c(best.scales, best.scale)
}

hist(best.scales)
hist(best.scales, 40)
hist(log10(best.scales))
hist(log10(best.scales), 40)

plot(sort(best.scales), type="l")
plot(sort(best.scales), type="l", log="x")
plot(sort(best.scales), type="l", log="y")
plot(sort(best.scales), type="l", log="xy")

