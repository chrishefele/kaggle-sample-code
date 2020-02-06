#
# rank-f7groups-test2.R by Chris Hefele, Jan 2016
# 

library("quantreg")

DATA.DIR            <- "../../data"
PLOT.FILE           <- "rank-f7groups-test2.pdf"
INTRADAY.TO.DAILY   <- 0.19
VERIFY.INTRADAY.TO.DAILY <- TRUE

#----------------------------------

read.file <- function(rdata.file) {
    fname <- paste(DATA.DIR, rdata.file, sep="/")
    cat("reading data from: ", fname, "\n")
    df <- readRDS(fname)
    df[is.na(df)] <- 0
    return(df)
}

print.sumabs.model <- function(df.raw, tag) {

    # The model of daily returns for stocks being used here is:  
    #
    #   abs(daily_return) = coef * sum(abs(intraday_returns))
    #
    # The coefficient is estimated using "rq" which performs quantile regression. 
    # Quantile regression (vs least-squares regression) is used because 
    # MAD (an L1 metric) is the evaluation metric,  not MSE (an L2 metric).
    # When using all stocks in a dataset, the coef seems pretty consistently 
    # about 0.19 across all data sets (i.e. train vs test1 vs test2).

    rm1 <- df.raw$Ret_MinusOne
    rm2 <- df.raw$Ret_MinusTwo 
    intraday.ret.cols <- paste("Ret_", c(2:120), sep="")
    returns        <- df.raw[, intraday.ret.cols]
    returns.sumabs <- apply(returns, 1, function(x) sum(abs(x)))

    cat(tag, " model coefficients (estimates of INTRADAY.TO.DAILY)\n")
    print( rq(abs(rm1) ~ 0 + returns.sumabs) )
    print( rq(abs(rm2) ~ 0 + returns.sumabs) )
    cat("\n")
}


print.sumabs.quantiles <- function(df.raw, tag) {
    taus <- c(0.05, 0.10, 0.15, 0.2, 0.25, 0.5, 0.75, 0.8, 0.85, 0.9, 0.95)
    rm2 <- df.raw$Ret_MinusTwo 
    intraday.ret.cols <- paste("Ret_", c(2:120), sep="")
    returns        <- df.raw[, intraday.ret.cols]
    returns.sumabs <- apply(returns, 1, function(x) sum(abs(x)))

    model <- rq(abs(rm2) ~ 0 + returns.sumabs, tau=0.5) 
    scale.median <- abs(coef(model)[["returns.sumabs"]])

    for(tau in taus) {
        model <- rq(abs(rm2) ~ 0 + returns.sumabs, tau=tau) 
        best.scale.sgnret <- abs(coef(model)[["returns.sumabs"]])
        relative.scale <- best.scale.sgnret / scale.median
        cat("model for quantile: ", tau, " for ", tag)
        cat(" scale: ", best.scale.sgnret)
        cat(" relative.scale: ", relative.scale, "\n")
    }
}


#----------------------------------

pdf(file=PLOT.FILE)

train <- read.file("train.RData")
test1 <- read.file("test.RData")
test2 <- read.file("test_2.RData")

if(VERIFY.INTRADAY.TO.DAILY) {
    print.sumabs.model(train, "training data")
    print.sumabs.model(test1, "test1 data")
    print.sumabs.model(test2, "test2 data")

    print.sumabs.quantiles(test2, "test2 data")
}

# test2 is a superset of test1
new.f7groups <- setdiff(unique(test2$Feature_7), unique(test1$Feature_7))

# stopifnot(FALSE)

# ----------------- scale optimization per group

best.scales <- c()
best.scale.sgnrets <- c()
cors.medians<- c()
score.deltas <- c()
f7rows <- c()

groups <- sort(unique(test2$Feature_7))

for(group in groups) {

    row.select  <- test2$Feature_7 == group
    col.select  <- paste("Ret_", c(2:120), sep="") 
    returns     <- test2[row.select, col.select ] 
    returns.sumabs <- apply(returns, 1, function(x) sum(   abs(x)))

    rm2  <- test2[ row.select, "Ret_MinusTwo" ]
    #rm2 <- test2[ row.select, "Ret_MinusOne" ]
    # rm2 <- if(median(rm2)>0) {rm2} else {-rm2} # pos median guarantees pos slope

    model <- rq( abs(rm2) ~ 0 + returns.sumabs ) 
    best.scale <- coef(model)[["returns.sumabs"]]
    
    model <- rq( rm2 ~ 0 + returns.sumabs ) 
    best.scale.sgnret <- abs(coef(model)[["returns.sumabs"]])

    # use rank correlation to reduce the impact of noise/outliers
    cors.median <- median(c(cor(t(returns), method="spearman"))) 

    score.delta <- sum(returns.sumabs) * INTRADAY.TO.DAILY * sqrt(cors.median)

    s <- sprintf("group %8i best.scale %7.4f best.scale.sgnret %7.4f cors.median %7.4f score.delta %7.4f", 
                    group, best.scale, best.scale.sgnret, cors.median, score.delta)
    cat(s, "\n")

    best.scales             <- c(best.scales,  best.scale)
    best.scale.sgnrets      <- c(best.scale.sgnrets,  best.scale.sgnret)
    cors.medians            <- c(cors.medians, cors.median)
    score.deltas            <- c(score.deltas, score.delta)
    f7rows                  <- c(f7rows, nrow(returns))

}

# --------- tables -----------

group.info <- data.frame(   groups, 
                            scale.abs=best.scales, scale.sgn=best.scale.sgnrets, 
                            cors.medians, f7rows, score.deltas )
group.info[,"new.F7"] <- groups %in% new.f7groups

cat("\nGroup info sorted by score.delta\n")
print(head(group.info[order(group.info$score.delta, decreasing=TRUE),], 20))
cat("\nGroup info sorted by cors.median\n")
print(head(group.info[order(group.info$cors.medians, decreasing=TRUE),], 20))

# --------- plots -----------

hist(score.deltas, 50)
hist(log10(score.deltas), 50)
plot(sort(score.deltas, decreasing=TRUE), type="b")
plot(sort(score.deltas, decreasing=TRUE), type="b", log="x")

hist(best.scales)
hist(best.scales, 40)
hist(log10(best.scales))
hist(log10(best.scales), 40)

plot(sort(best.scales), type="l")
plot(sort(best.scales), type="l", log="x")
plot(sort(best.scales), type="l", log="y")
plot(sort(best.scales), type="l", log="xy")

plot(cors.medians, best.scale.sgnrets, 
    xlab="cors.median", ylab="best.scale.sgnrets")
lines(lowess(cors.medians, best.scale.sgnrets, f=1./5), col="blue")

plot(cors.medians, best.scale.sgnrets/INTRADAY.TO.DAILY, 
    xlab="cors.median", ylab="best.scale.sgnrets/INTRADAY.TO.DAILY")
lines(lowess(cors.medians, best.scale.sgnrets/INTRADAY.TO.DAILY, f=1./5), col="blue")
lines(cors.medians, sqrt(cors.medians), col="green")

plot(cors.medians, best.scale.sgnrets, xlab="cors.median", ylab="best.scale.sgnrets", log="x")
lines(lowess(cors.medians, best.scale.sgnrets, f=1./5), col="blue")

plot(cors.medians, best.scale.sgnrets, xlab="cors.median", ylab="best.scale.sgnrets", log="y")
lines(lowess(cors.medians, best.scale.sgnrets, f=1./5), col="blue")

plot(cors.medians, best.scale.sgnrets, xlab="cors.median", ylab="best.scale.sgnrets", log="xy")
lines(lowess(cors.medians, best.scale.sgnrets, f=1./5), col="blue")

# ----------------

plot(best.scales, best.scale.sgnrets, xlab="best.scales", ylab="best.scale.sgnrets", pch=".")
lines(lowess(best.scales, best.scale.sgnrets, f=1./5), col="blue")

scale.ratios <- best.scale.sgnrets / best.scales

plot(cors.medians, scale.ratios, xlab="cors.medians", ylab="scale.ratios", pch=".")
lines(lowess(cors.medians, scale.ratios, f=1./5), col="blue")

plot(  cors.medians, best.scales, xlab="cors.medians", ylab="scales", pch=".", col="red")
points(cors.medians, best.scale.sgnrets, pch=".", col="blue")
lines(lowess(cors.medians, best.scales,        f=1./5), col="red")
lines(lowess(cors.medians, best.scale.sgnrets, f=1./5), col="blue")

#------------------------

cat("\nHigh-correlation group models\n")
groups.highcor <- groups[cors.medians > 0.5]
row.select <- test2[,"Feature_7"] %in% groups.highcor
test2.highcor <- test2[row.select,]
print.sumabs.quantiles(test2.highcor, "test2_cor>0.5")

