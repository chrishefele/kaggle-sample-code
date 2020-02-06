# waypoint_stats.R -- plot distribution of number of filed flightplan waypoints 

TRAIN_DIR <- '/home/chefele/kaggle/FlightQuest2/download/train'
PLOT_FILE <- '../plots/waypoint_stats.pdf'

pdf(file=PLOT_FILE)
day_dirs <- list.dirs(path=TRAIN_DIR, full.names=TRUE, recursive=FALSE)

for(day_dir in day_dirs) {
    wpts_file <- paste(day_dir,'/ASDI/asdifpwaypoint.csv',sep='')
    cat(wpts_file,'\n')
    wpts <- read.csv(wpts_file)
    wpts_counts <- table(wpts$asdiflightplanid) # waypoints per flight
    cat('Flightplan Waypoints/Flight stats:\n')
    print(quantile(wpts_counts, c(0.50,0.75,0.8,0.9,0.95,0.98,0.99,0.999)))
    cat('max:', max(wpts_counts), '\n')
    hist(wpts_counts, 100, main='Histogram of Flightplan Waypoints per Flight')
    cat('\n\n')
}


