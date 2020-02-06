
library(MASS)

PLOT.FILE         <- "x.pdf"
N.GROUP.STOCKS    <- 74
N.TRIALS          <- 100000
#N.TRIALS          <- 1000
GROUP.CORS        <- c(0.7237)

cor.rnorm <- function(n.dim, n.samples, cor.const) {
    # returns a matrix with one n.dim sample per row, n.samples rows
    cor.matrix <- rep(cor.const, n.dim*n.dim)
    dim(cor.matrix) <- c(n.dim, n.dim)
    diag(cor.matrix) <- 1
    zero.means <- rep(0, n.dim)
    mvrnorm(n=n.samples, mu=zero.means, Sigma=cor.matrix)
}

pdf(file=PLOT.FILE)
# par(mfrow=c(2,3))

guesses <- c(0:100)/100. * 2.

for(group.cor in GROUP.CORS) {

    errs.guess <- c()
    errs.zero  <- c()
    guess.wins <- c()
    err.guess.wins <- c()
    err.guess.loses <- c()

    for(guess in guesses) {

        #x <- rnorm(NPTS)
        x <- cor.rnorm(N.GROUP.STOCKS, N.TRIALS, group.cor)

        err.guess.rows  <- pmin(rowMeans(abs(x-guess)), rowMeans(abs(x--guess)))
        err.zero.rows   <- rowMeans(abs(x-0))
        err.guess       <- mean(err.guess.rows)
        err.zero        <- mean(err.zero.rows)
        guess.win       <- mean( err.guess.rows <= err.zero.rows )
        err.guess.win   <- mean( err.guess.rows[err.guess.rows <= err.zero.rows] )
        err.guess.lose  <- mean( err.guess.rows[err.guess.rows >  err.zero.rows] )

        cat("group.cor: ", group.cor, "guess: ",   guess,     
            " err.guess: ", err.guess, " err.zero: ", err.zero,  
            " guess.win: ", guess.win, "\n")
        errs.guess <- c(errs.guess, err.guess)
        errs.zero  <- c(errs.zero , err.zero)
        guess.wins <- c(guess.wins, guess.win)
        err.guess.wins  <- c(err.guess.wins,  err.guess.win)
        err.guess.loses <- c(err.guess.loses, err.guess.lose)
    }

    tag <- paste("group.cor:", group.cor, "n.stocks:", N.GROUP.STOCKS)

    errs.ylim <- c(0.4, 1.2)
    xlim.mask <- guesses < 0.5

    plot(guesses, errs.guess, xlab="guess", ylab="error", type="l", main=tag, ylim=errs.ylim)
    lines(guesses, errs.zero, col="blue")

    plot(guesses[xlim.mask], errs.guess[xlim.mask], xlab="guess", ylab="error", type="l", main=tag)
    lines(guesses[xlim.mask], errs.zero[xlim.mask], col="blue")

    plot(guesses, guess.wins, xlab="guess", ylab="guess.wins fraction (vs 0 prediction)", 
                type="l", main=tag, ylim=c(0,1))

    plot(guesses[xlim.mask], guess.wins[xlim.mask], xlab="guess", ylab="guess.wins fraction (vs 0 prediction)", 
                type="l", main=tag)


    plot(guess.wins,  err.guess.wins, xlab="guess.wins fraction (vs 0 prediction)", 
            ylab="err.guess.wins", type="l", main=tag, xlim=c(0,1), col="green")
    lines(guess.wins, errs.zero, col="blue")

    plot(guesses,  err.guess.wins, xlab="guess", main="Errors given Win/Loss over pred=0",
            ylab="error", type="l", col="green", ylim=c(0,1))
    lines(guesses, err.guess.loses, lwd=2, col="red")

}
