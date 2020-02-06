

TEST_FLIGHTS <- '/home/chefele/kaggle/FlightQuest2/download/testFlightsRev3.csv'
PLOTFILE <- '../plots/testFlightsHists.pdf'
pdf(file=PLOTFILE)

cat('reading', TEST_FLIGHTS,'\n')
flights <- read.csv(TEST_FLIGHTS)


skiplist <- c('CutoffTime', 'ArrivalAirport', 'ScheduledArrivalTime')

# print(summary(flights))

for(nm in names(flights)) {
    if(nm %in% skiplist) {
        cat('skipping ', nm, '\n')
    } else {
        cat('plotting ', nm, '\n')
        hist(flights[,nm], 100, main=nm)
    }
}
cat('wrote plots to:', PLOTFILE, '\n')

