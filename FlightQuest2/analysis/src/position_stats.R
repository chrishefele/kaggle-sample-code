

TRAIN_DIR <- '/home/chefele/kaggle/FlightQuest2/download/train'
PLOT_FILE <- '../plots/position_stats.pdf'

pdf(file=PLOT_FILE)
day_dirs <- list.dirs(path=TRAIN_DIR, full.names=TRUE, recursive=FALSE)

acc_flight_ids <- c()

for(day_dir in day_dirs) {
    posn_file <- paste(day_dir,'/ASDI/asdiposition.csv',sep='')
    cat(posn_file,'\n')
    posn <- read.csv(posn_file)
    n_flights <- length(unique(posn$flighthistoryid))
    n_posns   <- nrow(posn)
    posn_per_flight <- n_posns / n_flights
    cat(n_flights,' flights ', n_posns,' positions ', posn_per_flight, 'positions/flight', '\n' )

    cur_flight_ids <- unique(posn$flighthistoryid)
    overlap        <- intersect( cur_flight_ids, acc_flight_ids)
    acc_flight_ids <- union(acc_flight_ids,  cur_flight_ids)
    n_overlap <- length(overlap)
    n_flight_ids <- length(acc_flight_ids)
    cat(n_overlap,' previously-seen flight IDs; total ids is now:', n_flight_ids,'\n')

    cat('data summary\n')
    print(summary(posn))

    flt_wpts <- table(posn$flighthistoryid) # waypoints per flight
    cat('num waypoint median:', median(flt_wpts), 'max:', max(flt_wpts), '\n')
    print(quantile(flt_wpts, c(0.50,0.75,0.8,0.9,0.95,0.98,0.99,0.999)))
    hist(flt_wpts, 100, main='Histogram of Waypoints per Flight')

    cat('\n\n')

}

#file: asdi_positions.csv
#TRAIN_DIR <- '/home/chefele/kaggle/FlightQuest2/download/train/2013_07_01/ASDI'

#received,callsign,altitude,groundspeed,latitudedegrees,longitudedegrees,flighthistoryid
#2013-07-01 01:23:55-07,GPD668,15000,0,41.4199981689453,-73.120002746582,301759419
#2013-07-01 01:24:55-07,GPD668,15000,0,41.3800010681152,-73.0999984741211,301759419
#2013-07-01 01:25:55-07,GPD668,15000,0,41.3800010681152,-73.0299987792969,301759419


