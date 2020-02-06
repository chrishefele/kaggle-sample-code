
library("reshape2")
library("dplyr")
library("data.table")

#RETURNS.FILE            <- "../data/train.RData" # OR ../data/test.RData
RETURNS.FILE            <- "../data/test.RData" 
PROBES.DIR              <- "../probes"

INTRADAY.RETURNS.COLS   <- 2:120 
GROUP.COL               <- "Feature_7"
N.PROBE.GROUPS          <- 50   # write 1 set of 4 probe files per group
SCALE.SUMABS.TO.DAILY   <- 0.18 # empirical; scales sumabs intraday returns to 
                                # the estimated abs daily return magnitude
PROBE.SCALE.SUMABS      <- 5    # scaleup of estimated daily return magnitude

N.STOCKS                <- 60000
N.PREDS.PER.STOCK       <- 62
N.PREDS                 <- N.STOCKS * N.PREDS.PER.STOCK

get.returns <- function(df, ret.nums) {
    # Extracts intra-day stock returns from a dataframe read from the .csv
    # Returned matrix has one column per stock, one row per intra-day minute
    ret.col.names <- paste("Ret", as.character(ret.nums), sep="_")
    returns.df            <- df[,ret.col.names]
    row.names(returns.df) <- df[,"Id"]
    #row.names(returns.df) <- paste("Id", df[,"Id"], sep="_")
    return( t(returns.df) )
}

sorted.cors <- function(ret.A, ret.B) {
    corAB  <- cor(ret.A, ret.B)
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


make.write.probe <- function() {

    # for speed, create a closure, so only have to generate
    # submission.Id.dt once (it takes seconds to create)
    submission.Id.dt <- make.submission.Id.dt()

    write.probe.func <- function(seq.number, group.key, returns.df, 
                            probe.scale.sumabs, pred.col)       {

        stopifnot(pred.col %in% c(61, 62))

        group.select    <- returns.df[,GROUP.COL] == group.key 
        stock.Ids       <- returns.df[group.select, "Id"]
        ret.sumabs      <- returns.df[group.select, "SumAbsIntradayReturns"]
        pred.Id         <- paste(stock.Ids, pred.col, sep="_")
        pred.return     <- ret.sumabs * SCALE.SUMABS.TO.DAILY * probe.scale.sumabs 
        group.dt        <- data.table(Id=pred.Id, Predicted=pred.return)

        probe.dt <- merge(group.dt, submission.Id.dt, by="Id", all=TRUE, sort=FALSE)
        setkey(probe.dt, Ordering) # sorts by Ordering, instead of by Id
        probe.dt$Ordering <- NULL
        probe.dt[is.na(probe.dt)] <- 0

        probe.filename <- sprintf("probe_%04i_f7_%i_scale_%+i_pred_%i.csv", 
                                   seq.number, group.key, probe.scale.sumabs, pred.col)
        probe.path <- paste(PROBES.DIR, probe.filename, sep="/")
        cat("     writing: [", probe.path, "] ")
        write.csv(probe.dt, file=probe.path, row.names=FALSE, quote=FALSE)
        cat("\n")
    } # end of function

    return(write.probe.func)  # return function, closed over submission.Id.dt
} 
write.probe <- make.write.probe() 


main <- function() {

    cat("\n*** Probe File Generator for Winton Stock Market Challenge ***\n")

    returns <- readRDS(RETURNS.FILE)
    returns[is.na(returns)] <- 0 

    intraday.select <- paste("Ret_", INTRADAY.RETURNS.COLS, sep="")
    returns$SumAbsIntradayReturns <- 
        apply(returns[,intraday.select], 1, function(x) sum(abs(x)) )

    cors.medians <- c()

    group.keys <- sort(unique(returns[,GROUP.COL]))
    #group.keys <- group.keys[1:N.PROBE.GROUPS] # *** TODO REMOVE AFTER TESTING ***

    # determine the order of the groups, sorting by median correlation 
    # between pairs of stocks in the group
    cat("\nCalculating Feature_7 Group correlations\n\n")
    for(group.key in group.keys) {

        group.select  <- returns[,GROUP.COL] == group.key 
        returns.group <- get.returns(returns[group.select,], INTRADAY.RETURNS.COLS)

        cors.median   <- median(sorted.cors(returns.group, returns.group))
        cors.medians  <- c(cors.medians, cors.median)

        cat("Feature_7 group: ", group.key, " cors.median: ", cors.median, "\n")
    }

    cat("\n\nWriting Feature_7 Group probe files\n")

    probe.group.keys <- group.keys[order(cors.medians, decreasing=TRUE)]
    probe.group.keys <- probe.group.keys[1:N.PROBE.GROUPS]
    seq.number <- 0

    for(group.key in probe.group.keys) {

        group.select  <- returns[,GROUP.COL] == group.key 
        group.size    <- sum(group.select)
        returns.group <- get.returns(returns[group.select,], INTRADAY.RETURNS.COLS)
        cors.median   <- median(sorted.cors(returns.group, returns.group))
        cat("\nFeature_7 group: ", group.key, 
            " cors.median: ", cors.median, 
            " group.size: ", group.size, "\n")

        for(pred.col in c(61, 62)) {
            for(probe.scale.sumabs in c(-PROBE.SCALE.SUMABS, PROBE.SCALE.SUMABS)) {
                seq.number <- seq.number + 1
                write.probe(seq.number, group.key, returns,  probe.scale.sumabs, pred.col)
            }
        }
    }
}

main()

