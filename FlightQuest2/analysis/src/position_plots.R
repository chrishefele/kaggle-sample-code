# position_plots.R

library(maps)
library(geosphere)

TEST_MODE   <- FALSE
TRAIN_DIR   <- '/home/chefele/kaggle/FlightQuest2/download/train'
PLOT_FILE   <- '../plots/position_plots.pdf'
if(TEST_MODE) { PLOT_FILE <- '../plots/position_plots_TEST.pdf' }
FH_PER_DAY  <- 20 # flight histories to plot per day
NA_XLIM     <- c(-179, -30)
NA_YLIM     <- c(  15,  70)
RNG_SEED    <- 42
MIN_MAP_SIDE <- 1.0 # minimum degrees for lat/lon side of map

map_flightpath <- function(lats, lons, posn_start, posn_end, xlim, ylim) {
    map('world', col='#f2f2f2', fill=TRUE, bg='white', lwd=0.05, xlim=xlim, ylim=ylim)
    map.axes()
    # add great-circle path (blue dashed line) & actual path (red)
    lines(gcIntermediate(posn_start, posn_end, n=20, addStartEnd=TRUE), col='blue', lty=5)
    lines(lons, lats, col='red')
}

flighthistory_plots <- function(posn, tag) {

    posn_t <- strptime( paste(posn$received,'00',sep=''), format="%Y-%m-%d %H:%M:%S%z" )
    posn   <- posn[order(posn_t),]
    lats   <- posn$latitudedegrees
    lons   <- posn$longitudedegrees
    xlim   <- c( min(lons), max(min(lons)+MIN_MAP_SIDE, max(lons)) )
    ylim   <- c( min(lats), max(min(lats)+MIN_MAP_SIDE, max(lats)) )
    n      <- nrow(posn)
    posn_start <- c(lons[1], lats[1])
    posn_end   <- c(lons[n], lats[n])

    pin_original <- par()$pin # save plot dimentions
    map_flightpath(lats, lons, posn_start, posn_end, NA_XLIM, NA_YLIM)
    map_flightpath(lats, lons, posn_start, posn_end, xlim,    ylim)
    par(pin=pin_original) # restore, since map plots change them

    # plot altitude & velocity vs TIME
    #plot(posn_t, posn$altitude,    type='s', xlab='time', ylab='feet', main=paste('Altitude',   tag))
    #plot(posn_t, posn$groundspeed, type='s', xlab='time', ylab='mph',  main=paste('Groundspeed',tag))

    # plot altitude & velocity vs DISTANCE from origin, then velocity vs altitude
    dists <- distHaversine(posn_start, cbind(lons,lats), r=3963.1676) # r=earth radius in statute miles
    plot(dists, posn$altitude,    type='s', xlab='miles', ylab='feet', main=paste('Altitude - ',   tag))
    plot(dists, posn$groundspeed, type='s', xlab='miles', ylab='mph',  main=paste('Groundspeed - ',tag))
    plot(posn$altitude, posn$groundspeed, type='p', 
         xlab='alt(ft)', ylab='mph',  main=paste('Groundspeed vs. Altitude - ',tag))
    plot(posn$groundspeed, posn$altitude, type='p', 
         ylab='alt(ft)', xlab='mph',  main=paste('Altitude vs. Groundspeed - ',tag))
}

main <- function() {
    pdf(file=PLOT_FILE)
    par(mfrow=c(3,2))
    set.seed(RNG_SEED)

    day_dirs  <- list.dirs(path=TRAIN_DIR, full.names=TRUE, recursive=FALSE)
    day_files <- paste(day_dirs,'/ASDI/asdiposition.csv',sep='')
    if(TEST_MODE) {
        day_files <- day_files[1]
    }
    for(day_file in day_files) {
        cat('processing: ', day_file,'\n')
        posn <- read.csv(day_file)
        fhids <- sample(unique(posn$flighthistoryid), FH_PER_DAY)
        cat('plotting flight history:\n') 
        for(fhid in fhids) {
            cat(' ', fhid, '\n')
            plot_tag <- paste('FlightID:', as.character(fhid))
            flighthistory_plots( posn[posn$flighthistoryid==fhid,], plot_tag )
        }
    }
    cat('wrote flighthistory plots to: ', PLOT_FILE, '\n')
}

main()

#received,callsign,altitude,groundspeed,latitudedegrees,longitudedegrees,flighthistoryid
#2013-07-01 01:23:55-07,GPD668,15000,0,41.4199981689453,-73.120002746582,301759419
#2013-07-01 01:24:55-07,GPD668,15000,0,41.3800010681152,-73.0999984741211,301759419
#2013-07-01 01:25:55-07,GPD668,15000,0,41.3800010681152,-73.0299987792969,301759419

