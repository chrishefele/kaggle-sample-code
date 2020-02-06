library(NMFN)

TRAIN_FEATURES  <- '../../download/test.csv'
PLOT_FILE       <- 'board-cell-ring-prob-plots.pdf'

pdf(file=PLOT_FILE)
par(mfrow=c(3,3))

cat('\nReading data files\n')
train_raw <- read.csv(TRAIN_FEATURES)
train_raw$id <- NULL

for(nDelta in 1:5) {
        cat('delta:',nDelta,'\n')
        train <- train_raw[train_raw$delta==nDelta,]
        train$id    <- NULL
        train$delta <- NULL
        board <- colMeans(train)
        n <- sqrt(length(board))
        dim(board) <- c(n,n)

        for(radius in 0:8) {
            a <- 1 +radius
            b <- 20-radius
            ring <- board[a,a:b] + board[a:b,b] + board[b,b:a] + board[b:a,a]
            tag <- paste('radius', as.character(radius), 'delta', as.character(nDelta))
            ylim.min <- if(radius==0) 0 else 0.45
            ylim.max <- 0.65
            plot(ring, type='b', ylim=c(ylim.min,ylim.max),  main=tag)
            #plot(ring-mean(ring), type='b',  main=tag)
        }
}
