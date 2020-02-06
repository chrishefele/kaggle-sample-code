library(NMFN)

TRAIN_FEATURES  <- '../../download/test.csv'
PLOT_FILE       <- 'board-centercells-prob-plots.pdf'

pdf(file=PLOT_FILE)
#par(mfrow=c(3,2))

cat('\nReading data files\n')
train_raw <- read.csv(TRAIN_FEATURES)
train_raw$id <- NULL

plot(c(), type='b', xlim=c(0,10), ylim=c(0.120,0.150), main=paste('meanCell vs radius'))
for(nDelta in 1:5) {
        train <- train_raw[train_raw$delta==nDelta,]
        train$id    <- NULL
        train$delta <- NULL
        board <- colMeans(train)
        n <- sqrt(length(board))
        dim(board) <- c(n,n)

        center.means <- c()
        for(radius in 0:9) {
            side <- (10-radius):(11+radius)
            board.center <- board[side, side]
            ylim.min <- if(radius==0) 0 else 0.45
            ylim.max <- 0.65
            tag <- paste('radius', as.character(radius), 'delta', as.character(nDelta))
            cat('delta: ', nDelta, ' radius: ', radius, ' mean_alive: ', mean(board.center),'\n')
            center.means <- c(center.means, mean(board.center))
        }
        lines(center.means, type='b')
}
