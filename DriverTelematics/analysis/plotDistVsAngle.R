library(hexbin)

DISTS_ANGLES_DIR <- '../data/drivers/dists.angles'

pdf(file='plotDistVsAngle.pdf')
par(mfrow=c(2,2))

stats.files <- list.files(path=DISTS_ANGLES_DIR, full.names=TRUE, recursive=FALSE)

for(stats.file in stats.files)
{
        cat('processing: ', stats.file, '\n')
        stats <- read.csv(stats.file)

        log.dist.t0 = log10(stats$dist0)
        log.dist.t1 = log10(stats$dist1)
        angle.t0    = stats$angle0
        angle.t1    = stats$angle1

        smoothScatter(log.dist.t0, log.dist.t1)
        smoothScatter(log.dist.t0, angle.t0,  )
        smoothScatter(angle.t0,    log.dist.t1)
        smoothScatter(angle.t0,    angle.t1,  )

        #plot(hexbin(log.dist.t0, log.dist.t1))
        #plot(hexbin(log.dist.t0, angle.t0))
        #plot(hexbin(angle.t0,    log.dist.t1))
        #plot(hexbin(angle.t0,    angle.t1))
}

