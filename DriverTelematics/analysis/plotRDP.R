
TRACK_FILES_NUM <- 200
TRACK_FILES_DIR <- '../data/drivers/trips.rdp'

read.trackfile <- function(fdir, track.id, suffix) {
        fcsv <- paste(fdir, '/', as.character(track.id), suffix, sep='')
        read.csv(fcsv)
}

pdf(file="plotRDP.pdf")
par(mfrow=c(2,2))

driver.dirs <- list.dirs(path=TRACK_FILES_DIR, full.names=TRUE, recursive=FALSE)
driver.dirs <- driver.dirs[1:10]

for(driver.dir in driver.dirs) 
{
    for(track.file.id in c(1:TRACK_FILES_NUM)) {
        cat('processing: ', driver.dir, ' track: ', track.file.id, '\n')
        track <- read.trackfile(driver.dir, track.file.id, '.rdp.none.csv')

        x.range <-  max(track$x) - min(track$x) 
        y.range <-  max(track$y) - min(track$y)
        xy.range <- max(x.range, y.range)
        x.plotrange <- c( min(track$x), min(track$x)+ xy.range )
        y.plotrange <- c( min(track$y), min(track$y)+ xy.range )

        plot.title <- paste( "driver:", basename(driver.dir), 
                             "track:",  track.file.id,
                             "pts:", nrow(track) )

        plot(track$x, track$y, xlab='', ylab='', xlim=x.plotrange, ylim=y.plotrange, type='l', main=plot.title)

        track.dist      <- read.trackfile(driver.dir, track.file.id, '.rdp.dist.csv')
        track.angle     <- read.trackfile(driver.dir, track.file.id, '.rdp.angle.csv')
        track.distangle <- read.trackfile(driver.dir, track.file.id, '.rdp.distangle.csv')

        plot(track$x, track$y, xlab='', ylab='', xlim=x.plotrange, ylim=y.plotrange, type='l', 
                main=paste('RDP dist, pts:',nrow(track.dist) ), lty=2)
        lines(track.dist$x, track.dist$y, type='b', col="red", pch=20)

        plot(track$x, track$y, xlab='', ylab='', xlim=x.plotrange, ylim=y.plotrange, type='l', 
                main=paste('RDP angle, pts:', nrow(track.angle)),lty=2)
        lines(track.angle$x,track.angle$y, type='l', col="green", pch=20)

        plot(track$x, track$y, xlab='', ylab='', xlim=x.plotrange, ylim=y.plotrange, type='l', 
                main=paste('RDP distangle, pts:', nrow(track.distangle)), lty=2)
        lines(track.distangle$x, track.distangle$y, type='b', col="blue", pch=20)
    }
}

