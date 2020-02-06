# max_vs_dist.R

library(stats)
library(geosphere)

TEST_MODE   <- FALSE
TRAIN_DIR   <- '/home/chefele/kaggle/FlightQuest2/download/train'
PLOT_FILE   <- '../plots/max_vs_dist.pdf'
if(TEST_MODE) { PLOT_FILE <- '../plots/max_vs_dist_TEST.pdf' }

main <- function() {
    pdf(file=PLOT_FILE)
    par(mfrow=c(2,2))

    day_dirs  <- list.dirs(path=TRAIN_DIR, full.names=TRUE, recursive=FALSE)
    day_files <- paste(day_dirs,'/ASDI/asdiposition.csv',sep='')
    if(TEST_MODE) { day_files <- day_files[1] }

    for(day_file in day_files) {
        cat('processing: ', day_file,'\n')
        posn    <- read.csv(day_file)
        #posn_t <- strptime( paste(posn$received,'00',sep=''), format="%Y-%m-%d %H:%M:%S%z" )
        posn_ix    <- 1:nrow(posn)
        posn_ixmin <- tapply(posn_ix, posn$flighthistoryid, min)
        posn_ixmax <- tapply(posn_ix, posn$flighthistoryid, max)

        lats1   <- posn[posn_ixmin,'latitudedegrees']
        lons1   <- posn[posn_ixmin,'longitudedegrees']
        lats2   <- posn[posn_ixmax,'latitudedegrees']
        lons2   <- posn[posn_ixmax,'longitudedegrees']

        flight_dist <- distHaversine( cbind(lons1, lats1), 
                                      cbind(lons2, lats2), r=3963.1676 ) # in miles

        max_alt  <- tapply(posn$altitude,    posn$flighthistoryid, max)
        max_gspd <- tapply(posn$groundspeed, posn$flighthistoryid, max)

        PCH <- '.'
        YLIM_ALT  <- c(0, 45000)
        YLIM_GSPD <- c(0, 600)
        XLIM_DIST <- c(0,1000)
        scatter.smooth(flight_dist, max_alt,  type='n', ylim=YLIM_ALT, 
                pch=PCH, main="MaxAltitude vs FlightDistance")
        scatter.smooth(flight_dist, max_alt,  type='n', xlim=XLIM_DIST, ylim=YLIM_ALT, 
                pch=PCH, main="MaxAltitude vs FlightDistance")
        scatter.smooth(flight_dist, max_gspd, type='n', ylim=YLIM_GSPD,
                pch=PCH, main="MaxGroundspeed vs FlightDistance")
        scatter.smooth(flight_dist, max_gspd, type='n', xlim=XLIM_DIST, ylim=YLIM_GSPD,
                pch=PCH, main="MaxGroundspeed vs FlightDistance")

   }
   cat('wrote flighthistory plots to: ', PLOT_FILE, '\n')
}

main()

#received,callsign,altitude,groundspeed,latitudedegrees,longitudedegrees,flighthistoryid
#2013-07-01 01:23:55-07,GPD668,15000,0,41.4199981689453,-73.120002746582,301759419
#2013-07-01 01:24:55-07,GPD668,15000,0,41.3800010681152,-73.0999984741211,301759419
#2013-07-01 01:25:55-07,GPD668,15000,0,41.3800010681152,-73.0299987792969,301759419

