# altgspd_vs_dist.R

library(stats)
library(geosphere)

TEST_MODE   <- TRUE
TRAIN_DIR   <- '/home/chefele/kaggle/FlightQuest2/download/train'
PLOT_FILE   <- '../plots/altgspd_vs_dist.pdf'
if(TEST_MODE) { PLOT_FILE <- '../plots/altgspd_vs_dist_TEST.pdf' }
DIST_BIN_SIZE <- 100  # width in miles of flight distance bins for grouping data for plots

main <- function() {
    pdf(file=PLOT_FILE)
    par(mfrow=c(2,2))

    day_dirs  <- list.dirs(path=TRAIN_DIR, full.names=TRUE, recursive=FALSE)
    day_files <- paste(day_dirs,'/ASDI/asdiposition.csv',sep='')
    if(TEST_MODE) { day_files <- day_files[1:2] }

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

        flight_dist     <- distHaversine( cbind(lons1, lats1), cbind(lons2, lats2), r=3963.1676 ) # in miles
        flight_dist_bin <- as.integer(round(flight_dist/DIST_BIN_SIZE)*DIST_BIN_SIZE)

        #received,callsign,altitude,groundspeed,latitudedegrees,longitudedegrees,flighthistoryid

        flight_dists <- data.frame( flighthistoryid=rownames(posn_ixmin), 
                                    flight_dist=flight_dist, 
                                    flight_dist_bin=flight_dist_bin, 
                                    lon_start=lons1, 
                                    lat_start=lats1)
        df <- merge(x=posn, y=flight_dists, by='flighthistoryid')
        df$dist_from_start <- distHaversine( cbind(df$longitudedegrees, df$latitudedegrees), 
                                             cbind(df$lon_start,        df$lat_start), r=3963.1676 ) # in miles
        print(head(df))

        for(dist_bin in sort(unique(df$flight_dist_bin))) {
            tag <- paste('DistBin:', as.character(dist_bin))
            cat(tag,'\n')

            mask        <- df$flight_dist_bin==dist_bin  # TODO mask posn$flight_dist_bin, not flight_dist_bin 
            altitudes   <- df$altitude[mask]
            groundspeeds<- df$groundspeed[mask]
            dist_from_start <- df$dist_from_start[mask]

            PCH <- '.'
            YLIM_ALT  <- c(0, 45000)
            YLIM_GSPD <- c(0, 600)
            XLIM_DIST <- c(0,1000)
            # TODO plot posn$flight_dist[mask], not flight_dist
            scatter.smooth(dist_from_start, altitudes,    type='n', ylim=YLIM_ALT,                 pch=PCH, main=tag)
            scatter.smooth(dist_from_start, altitudes,    type='n', xlim=XLIM_DIST, ylim=YLIM_ALT, pch=PCH, main=tag)
            scatter.smooth(dist_from_start, groundspeeds, type='n', ylim=YLIM_GSPD,                pch=PCH, main=tag)
            scatter.smooth(dist_from_start, groundspeeds, type='n', xlim=XLIM_DIST, ylim=YLIM_GSPD,pch=PCH, main=tag)
        }

   }
   cat('wrote plots to: ', PLOT_FILE, '\n')
}

main()

#received,callsign,altitude,groundspeed,latitudedegrees,longitudedegrees,flighthistoryid
#2013-07-01 01:23:55-07,GPD668,15000,0,41.4199981689453,-73.120002746582,301759419
#2013-07-01 01:24:55-07,GPD668,15000,0,41.3800010681152,-73.0999984741211,301759419
#2013-07-01 01:25:55-07,GPD668,15000,0,41.3800010681152,-73.0299987792969,301759419

