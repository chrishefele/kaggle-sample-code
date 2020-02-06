
pdf(file="opt-scale-of-sumabs-or-const-vs-dailyret.pdf")

library("quantreg")

train <- readRDS("../data/train.RData")
train[is.na(train)] <- 0

# ----------------- global scale optimization

rp2 <- train$Ret_PlusTwo
rp2[is.na(rp2)] <- 0 
rp2.abs <- abs(rp2)

calc.errs <- function(group.id, y, x.df) {

    returns             <- x.df[, paste("Ret_", c(2:120), sep="")]
    returns.sumabs      <- apply(returns, 1, function(x) sum(abs(x)) )

    model.sumabs      <- rq(  y ~ 0 + returns.sumabs)
    best.scale.sumabs <- coef(model.sumabs)[["returns.sumabs"]]

    model.const       <- rq(  y ~ 1)
    best.scale.const  <- coef(model.const)[["(Intercept)"]]

    model.zero        <- 0

    preds.sumabs      <- best.scale.sumabs * returns.sumabs
    preds.const       <- best.scale.const  * 1
    preds.zero        <- 0

    errs.sumabs <- sum(abs( preds.sumabs - y )) 
    errs.const  <- sum(abs( preds.const  - y )) 
    errs.zero   <- sum(abs( preds.zero   - y )) 
    pct.sumabs.vs.zero <- errs.sumabs / errs.zero 

    cat("  group.id: ", group.id) 
    cat("  median  : ", median(returns.sumabs))
    cat("  errs.sumabs: ", errs.sumabs)
    cat("  errs.const : ", errs.const )
    cat("  errs.zero  : ", errs.zero  , "\n")
    cat("  pct.sumabs.vs.zero : ", pct.sumabs.vs.zero, "\n")


    return( list(   scale=best.scale.sumabs, 
                    errs=c(errs.sumabs, errs.const, errs.zero)))

} 

calc.errs(0, rp2.abs, train)

# ----------------- scale optimization per group

errs <- 0
best.scales <- c()
for(group in unique(train$Feature_7)) {

    row.select  <- train$Feature_7 == group
    returns     <- train[row.select, ]

    rp2.abs     <- abs(train[row.select, "Ret_PlusTwo" ])
   
    result <- calc.errs(group, rp2.abs, returns)
    errs        <- errs         + result$errs
    best.scales <- c(best.scales, result$scale)

    print(errs)

}

hist(best.scales, 50)

h <- hist(best.scales, 50, plot=FALSE)
plot(h$counts, type="b")
h$counts <- h$counts / sum(h$counts) * c(1:length(h$counts))
plot(h$counts, type="b")

hist(log10(best.scales), 50)

