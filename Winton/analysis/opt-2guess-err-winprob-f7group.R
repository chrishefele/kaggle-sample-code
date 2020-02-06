
library(MASS)

TEST2.FILE        <- "../data/test_2.RData"
PLOT.FILE         <- "opt-2guess-err-winprob-f7group.pdf"

BEST.F7.GROUP     <- 75916
N.TRIALS          <- 100000
VERBOSE           <- TRUE

get.test2 <- function() {
    cat("Now  reading: ", TEST2.FILE, "\n")
    test2 <- readRDS(TEST2.FILE)
    cat("Done reading: ", TEST2.FILE, "\n")
    test2[is.na(test2)] <- 0
    rownames(test2) <- paste("Id", test2$Id, sep="_")
    return(test2)
}

group.cov.matrix <- function(f7group, test2) {
    col.select <- paste("Ret", 2:120, sep="_")
    row.select <- test2$Feature_7  == f7group
    rets       <- test2[row.select, col.select]
    cov.mat    <- cov(t(rets)) 
    cov.mat.norm <- cov.mat / median(diag(cov.mat))  # TODO norm some other way???
    #plot(sort(diag(cov.mat.norm)))
    return(cov.mat.norm)
}

group.rnorm <- function(n.samples, grp.cov.mat) {
    # returns a matrix with one n.dim sample per row, n.samples rows
    stopifnot( nrow(grp.cov.mat) == ncol(grp.cov.mat) ) 
    zero.means <- rep(0, nrow(grp.cov.mat))
    mvrnorm(n=n.samples, mu=zero.means, Sigma=grp.cov.mat, empirical=TRUE)
}

main <- function() {

    pdf(file=PLOT.FILE)
    par(mfrow=c(2,2))

    test2 <- get.test2()
    group.ids <- c(BEST.F7.GROUP)
    #group.ids <- c(BEST.F7.GROUP, sort(unique(test2$Feature_7)))

    for(group.id in group.ids) {

        x <- group.rnorm(N.TRIALS, group.cov.matrix(group.id, test2)) 

        errs.guess      <- c()
        errs.zero       <- c()
        guess.wins      <- c()
        err.guess.wins  <- c()
        err.guess.loses <- c()

        guesses <- c(0:100)/100. * 2.
        for(guess in guesses) {

            err.guess.rows  <- pmin(rowMeans(abs(x-guess)), rowMeans(abs(x--guess)))
            err.zero.rows   <- rowMeans(abs(x-0))
            err.guess       <- mean(err.guess.rows)
            err.zero        <- mean(err.zero.rows)
            #guess.win       <- mean( err.guess.rows <= err.zero.rows )
            win.mask        <- err.zero.rows - err.guess.rows >= 0.0   # NEWNEWNEW NOTE *******
            guess.win       <- mean( win.mask )
            err.guess.win   <- mean( err.guess.rows[ win.mask] )
            err.guess.lose  <- mean( err.guess.rows[!win.mask] )

            if(VERBOSE) {
                cat("f7.group: "  , group.id,  " guess: ",   guess,     
                    " err.guess: ", err.guess, " err.zero: ", err.zero,  
                    " guess.win: ", guess.win, "\n")
            }

            errs.guess      <- c(errs.guess, err.guess)
            errs.zero       <- c(errs.zero , err.zero)
            guess.wins      <- c(guess.wins, guess.win)
            err.guess.wins  <- c(err.guess.wins,  err.guess.win)
            err.guess.loses <- c(err.guess.loses, err.guess.lose)
        }

        cat("***** Plotting Feature_7 Group: ", group.id, " *****\n")
        tag <- paste("F7:", group.id)

        errs.ylim <- c(0.5, 1.5)
        xlim.mask <- guesses < 0.5

        plot(guesses, errs.guess, xlab="guess", ylab="error", type="l", main=tag, ylim=errs.ylim)
        lines(guesses, errs.zero, col="blue")

        plot(guesses,  err.guess.wins, xlab="guess", main="Errors given Win/Loss over pred=0",
                ylab="error", type="l", col="green", ylim=c(0,1.5))
        lines(guesses, err.guess.loses, lwd=2, col="red")

        #plot(guesses[xlim.mask], errs.guess[xlim.mask], xlab="guess", ylab="error", type="l", main=tag)
        #lines(guesses[xlim.mask], errs.zero[xlim.mask], col="blue")

        plot(guesses, guess.wins, xlab="guess", ylab="guess.wins fraction (vs 0 prediction)", 
                    type="l", main=tag, ylim=c(0,1))

        plot(guesses[xlim.mask], guess.wins[xlim.mask], xlab="guess", ylab="guess.wins fraction (vs 0 prediction)", 
                    type="l", main=tag)
                    #type="l", main=tag, ylim=c(0.75, 1))

        #plot(guess.wins,  err.guess.wins, xlab="guess.wins fraction (vs 0 prediction)", 
        #        ylab="err.guess.wins", type="l", main=tag, xlim=c(0,1), col="green")
        #lines(guess.wins, errs.zero, col="blue")

    }
}

main()
