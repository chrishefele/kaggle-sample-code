load(file="/home/chefele/AlgoTrading/data/probe.Rsave")  # a hold out set; was the old testing set
load(file="/home/chefele/AlgoTrading/data/training.Rsave")

pdf(file="plot_securityid_counts.pdf")

plotSecurityProb <- function(ids, plottitle, cumulative) {
    sorted.security_id.probs <- sort( table(ids)/sum(table(ids)) )
    if(cumulative) { 
        sorted.security_id.probs <- cumsum(sorted.security_id.probs) 
    }
    plot(sorted.security_id.probs, main=plottitle)
}

par(mfrow=c(2,2))
plotSecurityProb(training$security_id, "Security_id distribution - TRAINING", FALSE)
plotSecurityProb(probe$security_id,    "Security_id distribution - PROBE (old testing)", FALSE)
plotSecurityProb(training$security_id, "Security_id cumulative distribution - TRAINING", TRUE)
plotSecurityProb(probe$security_id,    "Security_id cumulative distribution - PROBE (old testing)", TRUE)

