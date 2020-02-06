library(NMFN)

TRAIN_FEATURES  <- '../../download/test.csv'
PLOT_FILE       <- 'board-cell-prob-image.pdf'

pdf(file=PLOT_FILE)
par(mfrow=c(2,2))


mirror <- function(m) { 
    # create mirror image of matrix 
    t(m)[,nrow(m):1] 
} 

cat('\nReading data files\n')
train_raw <- read.csv(TRAIN_FEATURES)
train_raw$id <- NULL

for(nDelta in 1:5) {
        cat('delta:',nDelta,'\n')
        train <- train_raw[train_raw$delta==nDelta,]
        train$id    <- NULL
        train$delta <- NULL
        board.probs <- colMeans(train)
        n <- sqrt(length(board.probs))
        dim(board.probs) <- c(n,n)
        board.probs.diff <- board.probs - mean(board.probs)

        tag <- paste('board cell probs, delta=',as.character(nDelta))
        #image(board.probs, main=tag)
        cat('\n', tag,'\n')
        print(board.probs)
        cat('\n')
        print(board.probs.diff)

        # lines( (rowMeans(board.probs) + colMeans(board.probs))/2. ,type='b' )   
        image(board.probs)

        tag <- paste('delta=', as.character(nDelta))
        persp(board.probs, xlab='board rows', ylab='board columns',
                        zlab='cell alive probability', theta=30, phi=30, main=tag)

        plot(  diag(board.probs), ylim=c(0,0.16), type='b', main='board diag means')
        lines( diag(mirror(board.probs)), type='b' )   
        plot(  colMeans(board.probs), ylim=c(0,0.16), type='b', main='board row/col means')
        lines( rowMeans(board.probs), type='b' )   

}
