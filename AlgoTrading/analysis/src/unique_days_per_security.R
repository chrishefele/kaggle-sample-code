pdf(file="unique_days_per_security.pdf")

numUniqs <- function(x) { length(unique(x)) }
daycountPerSecurity <- function(dat) { tapply(dat$p_tcount, dat$security_id, numUniqs) }
plotDaycountPerSecurity <- function(dat,tag) { 
    title <- paste("Histogram of Unique Trading Days for Each Security", tag)
    hist(tapply(dat$p_tcount, dat$security_id, numUniqs),main=title )
}

load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
print(daycountPerSecurity(probe))
plotDaycountPerSecurity(probe, "Old_Testing/Holdout")

load(file="/home/chefele/AlgoTrading/data/testing.Rsave")
print(daycountPerSecurity(testing))
plotDaycountPerSecurity(testing, "Testing")

load(file="/home/chefele/AlgoTrading/data/training.Rsave")
print(daycountPerSecurity(training))
plotDaycountPerSecurity(training, "Training")

