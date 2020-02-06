
pdf(file="initial_stats.pdf")

tst <- read.csv("/home/chefele/AlgoTrading/download/Nov10/testing.csv")

parseHMS <- function(timeString) { strptime(timeString, format="%H:%M:%OS") }
parseHM  <- function(timeString) { strptime(timeString, format="%H:%M") }
t1  <- parseHMS( tst$time1  )
t50 <- parseHMS( tst$time50 )

par(mfrow=c(2,2))  # 2x2 grid of plots per page
hist(as.numeric(t50-t1)       ,200)
hist(log10(as.numeric(t50-t1)),200)
hist(as.numeric(t1 -min(t1 )) ,200)
hist(as.numeric(t50-min(t50)) ,200)

plotSpreadMeansVsTime <- function(asks, bids, times, plottitle,logplot) {
    spreads  <- as.vector(as.numeric(asks - bids))
    times.hm <- as.vector(as.numeric(parseHM(times)))
    spread.means.vs.time <- tapply(spreads, times.hm, mean)
    if(logplot) {
        plot(log10(spread.means.vs.time),ylim=c(-0.2,1.0), main=plottitle)
    } else {
        plot(spread.means.vs.time,main=plottitle)
    }
}

par(mfrow=c(3,3))  # 3x3 grid of plots per page
plotSpreadMeansVsTime(tst$ask1,   tst$bid1,   tst$time50,  "T=1   Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask10,  tst$bid10,  tst$time50,  "T=10  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask20,  tst$bid20,  tst$time50,  "T=20  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask30,  tst$bid30,  tst$time50,  "T=30  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask40,  tst$bid40,  tst$time50,  "T=40  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask45,  tst$bid45,  tst$time50,  "T=45  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask47,  tst$bid47,  tst$time50,  "T=47  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask48,  tst$bid48,  tst$time50,  "T=48  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask49,  tst$bid49,  tst$time50,  "T=49  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask50,  tst$bid50,  tst$time50,  "T=50  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask51,  tst$bid51,  tst$time50,  "T=51  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask52,  tst$bid52,  tst$time50,  "T=52  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask55,  tst$bid55,  tst$time50,  "T=55  Spreads", TRUE)
plotSpreadMeansVsTime(tst$ask60,  tst$bid60,  tst$time50,  "T=60  Spreads", TRUE) 
plotSpreadMeansVsTime(tst$ask70,  tst$bid70,  tst$time50,  "T=70  Spreads", TRUE) 
plotSpreadMeansVsTime(tst$ask80,  tst$bid80,  tst$time50,  "T=80  Spreads", TRUE) 
plotSpreadMeansVsTime(tst$ask90,  tst$bid90,  tst$time50,  "T=90  Spreads", TRUE) 
plotSpreadMeansVsTime(tst$ask100, tst$bid100, tst$time50,  "T=100 Spreads", TRUE) 

