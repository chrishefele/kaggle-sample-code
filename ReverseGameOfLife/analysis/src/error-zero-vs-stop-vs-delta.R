x <- read.csv('../../download/train.csv', as.is = T)
pdf(file="error-zero-vs-stop-vs-delta.pdf")

stop  <- x[,c(2, grep('stop', names(x)))]
start <- x[,c(2, grep('start', names(x)))]

stp  <- split(stop[,-1], stop$delta)
strt <- split(start[,-1], start$delta)

ss      <- seq(.001, .4, .005)
all.out <- c()

# par(mfcol = c(2, 3), mar = rep(2,4))

# Stratify by delta
for(i in 1:length(stp)){
  out       <- rep(NA, length(ss))
  startstop <- rep(NA, length(ss))
  startzero <- rep(NA, length(ss))

  # For each density in ss, compare performance of two methods
  for(j in 1:length(ss)){
    print(j)
    ap      <- apply(stp[[i]], 1, mean)
    sel     <- ap < (ss[j] + .005) &  ap > ss[j] 
    sstop   <- stp[[i]][sel,]
    sstart  <- strt[[i]][sel,]
 
    # Difference between "carry forward" and "all zeros"
    try(out[j] <- mean(sstop == sstart) - mean(0 == sstart))
    try( startstop[j] <- mean(sstop != sstart) )
    try( startzero[j] <- mean(    0 != sstart) )
  } 
  # plot(out, col = i, main = paste('delta:',i))
  plot(ss,  startstop, col = "red",   type="l", lty=2, ylim=c(0, 0.5), 
        ylab="mean cell error", xlab="board density", main = paste('delta:',i))
  lines(ss, startzero, col = "black", type="l" )
  all.out <- cbind(all.out, out)

}
