
ERR.STATS       <- '../data/cellerr.csv'
PLOT.FILE       <- 'cellerr.pdf'

pdf(file=PLOT.FILE)
par(mfrow=c(2,2))

cat('\nReading data files\n')
err.stats <- read.csv(ERR.STATS)

# delta, reg, row, col, cellerr
# 1, -1, 0, 0, 0.01043

deltas <- unique(err.stats$delta)
regs   <- unique(err.stats$reg)

for(delta in deltas) {
    for(reg in regs) {
        cat('delta: ', delta, ' reg: ', reg,'\n')
        mask <- (err.stats$delta == delta) & (err.stats$reg == reg)
        err  <- err.stats[mask,]$cellerr
        dim(err) <- c(20,20)
        tag <- paste('delta=',as.character(delta),'reg:', as.character(reg))
        image(err, main=tag)
        persp(err, xlab='board rows', ylab='board columns',
                        zlab='error probability', theta=30, phi=30, main=tag)
        persp(err, xlab='board rows', ylab='board columns',
                        zlab='error probability', theta=30, phi=30, main=tag)
        image(err, main=tag)
    }
}

