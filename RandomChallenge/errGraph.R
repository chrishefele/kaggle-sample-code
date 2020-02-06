#pdf(file="errGraph.pdf")

N        <- 1000
rands    <- sort(runif(N))
m        <- matrix( rep(rands, times=N), nrow=N, ncol=N)
mae      <- abs(m - t(m))
mae_vs_x <- colMeans(mae)

plot(   c(1:N)/N, mae_vs_x, 
        main='MAE vs X for Uniform Distribution on [0,1]', 
        xlab='X', ylab='MAE', type ='l'
)

cat('done\n')


