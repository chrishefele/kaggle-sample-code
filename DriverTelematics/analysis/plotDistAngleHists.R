DISTS_ANGLES_DIR <- '../data/drivers/dists.angles'

pdf(file='plotDistAngleHists.pdf')

par(mfrow=c(2,2))

stats.files <- list.files(path=DISTS_ANGLES_DIR, full.names=TRUE, recursive=FALSE)

for(stats.file in stats.files)
{
        cat('processing: ', stats.file, '\n')
        stats <- read.csv(stats.file)
        
        hist(stats$dist0, 
             main=paste('Dist Hist', basename(stats.file)), 40)

        hist(log10(stats$dist0), 
             main=paste('Log10 Dist Hist', basename(stats.file)),
             xlim=c(0.0, 6.0), 25 )

        hist(stats$angle0, 
             main=paste('Angle Hist', basename(stats.file)),
             xlim=c(-360, 360), 72 )

        hist(log10(stats$angle0), 
             main=paste('Log10 Angle Hist for', basename(stats.file)), 40)
}

