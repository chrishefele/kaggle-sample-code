# baseline scores for Heritage Health Prize
# by Chris Hefele

DATA_PATH <- "/home/chefele/HHP/download/HHP_release3/"
dih <- read.csv(paste(DATA_PATH,"DaysInHospital_Y2.csv",sep=""))

eps.score <- function(p,a) { sqrt(mean((log(p+1)-log(a+1))^2)) }

# all zeros
eps.score(0, dih$DaysInHospital)

# mean of days in hospital
plain.mean <- mean(dih$DaysInHospital)
print(plain.mean)
eps.score(plain.mean ,dih$DaysInHospital)

# all 15's 
eps.score(15,dih$DaysInHospital)

# mean of log(daysinhospital+1)_
log.mean <- mean( log(dih$DaysInHospital+1) ) 
log.mean.preds   <- exp(log.mean)-1 
print(log.mean.preds)
eps.score(log.mean.preds, dih$DaysInHospital)

# find threshold for worst possible prediction; >THRESH -> 0, else 15 (i.e. be as far as possible from the true value)
# Due to log scale, worst scores obtained when THRESH=2 or 3 (not midscale (7) on the linear scale!)
# (the "or" is because 3 equidistant from 15 & 0, based on the scoring metric log(x+1)^2 

worst.scores <- c()
worst.threshs <- c()
for(THRESH in 0:15) {
    worst.preds <- dih$DaysInHospital * 0
    mask <- dih$DaysInHospital > THRESH
    worst.preds[ mask] <- 0
    worst.preds[!mask] <- 15 
    trial.worst.score <- eps.score(worst.preds,dih$DaysInHospital)
    print( paste("Threshold:", as.character(THRESH),"Score:",as.character(trial.worst.score)))
    worst.scores <- c(worst.scores, trial.worst.score)
    worst.threshs<- c(worst.threshs, THRESH)
}
# plot(worst.threshs, worst.scores, type="b")



