
library("reshape2")
library("dplyr")
library("data.table")

RETURNS.FILE            <- "../data/test_2.RData" 
SUBMISSION.DIR          <- "../submissions/final2"

INTRADAY.RETURNS.COLS   <- 2:120 
GROUP.COL               <- "Feature_7"
N.SUB.GROUPS            <- 20   # write 1 set of 4 files per group
SCALE.SUMABS.TO.DAILY   <- 0.18 # empirical; scales sumabs intraday returns to 
                                # the estimated abs daily return magnitude
#SUB.SCALE.SUMABS       <- 0.3  # scaleup/shrinkage of estimated daily return magnitude
SUB.SCALE.SUMABS        <- 0.25 # scaleup/shrinkage of estimated daily return magnitude

N.STOCKS                <- 120000
N.PREDS.PER.STOCK       <- 62
N.PREDS                 <- N.STOCKS * N.PREDS.PER.STOCK

get.returns <- function(df, ret.nums) {
    # Extracts intra-day stock returns from a dataframe read from the .csv
    # Returned matrix has one column per stock, one row per intra-day minute
    ret.col.names <- paste("Ret", as.character(ret.nums), sep="_")
    returns.df            <- df[,ret.col.names]
    row.names(returns.df) <- df[,"Id"]
    return( t(returns.df) )
}

sorted.cors <- function(ret.A, ret.B) {

    # corAB  <- cor(ret.A, ret.B)
    # Instead of using Pearson correlation above, instead 
    # use Spearman rank correlation to improve noise/spike immunity
    corAB  <- cor(ret.A, ret.B, method="spearman") 

    melted <- melt(corAB, varnames=c("Id.A","Id.B"), value.name="corReturns")
    melted <- melted[(melted$Id.A != melted$Id.B), ]  # avoid cor=1 to same stock
    cors   <- melted$corReturns
    top.N  <- sort(cors, decreasing=TRUE)
    return(top.N)
}

make.submission.Id.dt <- function() {
    cat("\nInitializing ... ")
    submission    <- expand.grid(x=1:N.PREDS.PER.STOCK, y=1:N.STOCKS) # cartesian product
    submission$Id <- paste(submission$y, submission$x, sep="_") # <stock id>_<pred_col>
    submission$Ordering <- 1:nrow(submission)
    submission$x  <- NULL
    submission$y  <- NULL
    submission.dt <- data.table(submission)
    cat("done\n")
    return(submission.dt)
}

make.write.sub <- function() {

    # For speed, create a closure, so only have to generate
    # submission.Id.dt once (it takes seconds to create)
    submission.Id.dt <- make.submission.Id.dt()

    write.sub.func <- function(seq.number, group.key, returns.df, 
                            sub.scale.sumabs, pred.col)       {

        stopifnot(pred.col %in% c(61, 62))

        group.select    <- returns.df[,GROUP.COL] == group.key 
        stock.Ids       <- returns.df[group.select, "Id"]
        ret.sumabs      <- returns.df[group.select, "SumAbsIntradayReturns"]
        pred.Id         <- paste(stock.Ids, pred.col, sep="_")
        pred.return     <- ret.sumabs * SCALE.SUMABS.TO.DAILY * sub.scale.sumabs 
        group.dt        <- data.table(Id=pred.Id, Predicted=pred.return)

        sub.dt <- merge(group.dt, submission.Id.dt, by="Id", all=TRUE, sort=FALSE)
        setkey(sub.dt, Ordering) # sorts by Ordering, instead of by Id
        sub.dt$Ordering <- NULL
        sub.dt[is.na(sub.dt)] <- 0

        sub.filename <- sprintf("sub_%04i_f7_%i_scale_%+05.2f_pred_%i.csv", 
                                   seq.number, group.key, sub.scale.sumabs, pred.col)
        sub.path <- paste(SUBMISSION.DIR, sub.filename, sep="/")
        cat("     writing: [", sub.path, "] ")
        write.csv(sub.dt, file=sub.path, row.names=FALSE, quote=FALSE)
        cat("\n")
    } # end of function

    return(write.sub.func)  # return function, closed over submission.Id.dt
} 
write.sub <- make.write.sub() 


group.metrics <- function(returns, group.key) {

    group.select  <- returns[,GROUP.COL] == group.key 
    returns.group <- get.returns(returns[group.select,], INTRADAY.RETURNS.COLS)
    cors.median   <- median(sorted.cors(returns.group, returns.group))
    score.delta   <- sum(abs(returns.group)) * SCALE.SUMABS.TO.DAILY * sqrt(cors.median)
    group.size    <- sum(group.select)

    cat(sprintf("Feature_7_group: %7i group.size: %4i cors.median: %7.4f score.delta: %7.4f", 
                group.key, group.size, cors.median, score.delta), "\n")

    return( list("cors.median"=cors.median, "score.delta"=score.delta) ) 
}


main <- function() {

    cat("\n*** Submission File Generator for Winton Stock Market Challenge ***\n")

    returns <- readRDS(RETURNS.FILE)
    returns[is.na(returns)] <- 0 

    intraday.select <- paste("Ret_", INTRADAY.RETURNS.COLS, sep="")
    returns$SumAbsIntradayReturns <- 
        apply(returns[,intraday.select], 1, function(x) sum(abs(x)) )

    cors.medians <- c()
    score.deltas <- c()

    group.keys <- sort(unique(returns[,GROUP.COL]))

    # Write files for the top groups (ordered by score impact or correlation)

    cat("\nCalculating Feature_7 Group correlations and estimated score impacts\n\n")
    for(group.key in group.keys) {
        metrics       <- group.metrics(returns, group.key)
        cors.medians  <- c(cors.medians, metrics$cors.median)
        score.deltas  <- c(score.deltas, metrics$score.delta)
    }

    cat("\n\nWriting submission files for the top groups\n")
    sub.group.keys   <- group.keys[order(cors.medians, decreasing=TRUE)]
    #sub.group.keys  <- group.keys[order(score.deltas, decreasing=TRUE)]
    sub.group.keys  <- sub.group.keys[1:N.SUB.GROUPS]
    seq.number <- 0

    for(group.key in sub.group.keys) {
        cat("\n")
        group.metrics(returns, group.key) # just prints the metrics
        for(pred.col in c(61, 62)) {
            for(sub.scale.sumabs in c(-SUB.SCALE.SUMABS, SUB.SCALE.SUMABS)) {
                seq.number <- seq.number + 1
                write.sub(seq.number, group.key, returns,  sub.scale.sumabs, pred.col)
            }
        }
    }
}

main()

