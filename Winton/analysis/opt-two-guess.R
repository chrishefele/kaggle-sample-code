
# script to find the optmial two-guess strategy for getting as close
# as possible to a number drawn from a normal distribution (L1 errer / MAE)

pdf(file="opt-two-guess.pdf")

NPTS <- 1000000

guesses <- c(0:100)/100. * 2.

errs.guess <- c()
errs.zero  <- c()

for(guess in guesses) {

    x <- rnorm(NPTS)
    err.guess <- mean(pmin( abs(x - guess), abs(x - -guess) ))
    err.zero  <- mean(      abs(x - 0))
    cat("guess: ", guess, " err.guess: ", err.guess, "err.zero:", err.zero, "\n")
    errs.guess <- c(errs.guess, err.guess)
    errs.zero  <- c(errs.zero , err.zero)
}

plot(guesses, errs.guess, xlab="x", ylab="error", type="l")
lines(guesses, errs.zero)

