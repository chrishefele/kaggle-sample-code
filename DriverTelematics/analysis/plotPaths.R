
pdf(file="plotPaths.pdf")

par(mfrow=c(2,2))

driver.dirs <- list.dirs(path = "../download/drivers", full.names = TRUE, recursive = FALSE)
driver.dirs <- driver.dirs[1:10]

for(driver.dir in driver.dirs) 
{
    track.files <- list.files(path = driver.dir, full.names  = TRUE, no.. = TRUE)
    for(track.file in track.files) {
        cat('processing: ', track.file, '\n')
        track <- read.csv(track.file)

        x.range <-  max(track$x) - min(track$x) 
        y.range <-  max(track$y) - min(track$y)
        xy.range <- max(x.range, y.range)
        x.plotrange <- c( min(track$x), min(track$x)+ xy.range )
        y.plotrange <- c( min(track$y), min(track$y)+ xy.range )

        plot.title <- paste( "driver:", basename(driver.dir), 
                             "track:",  basename(track.file) )
        plot(track$x, track$y, 
             xlab='', ylab='', 
             xlim=x.plotrange, 
             ylim=y.plotrange, 
             type='l', main=plot.title)

        N <- length(track$x)
        points(track$x[1], track$y[1], pch=19)
        points(track$x[N], track$y[N], pch=22)

        radius <- sqrt( track$x^2 + track$y^2 )
        plot(radius, main="Radius", xlab="secs", ylab="", type="l")

        velocity <- sqrt( diff(track$x)^2 + diff(track$y)^2 )
        hist(velocity, main="Velocity Dist", 40)

        accel <- diff(velocity)
        hist(accel, main="Acceleration Dist", 40)


    }
}

