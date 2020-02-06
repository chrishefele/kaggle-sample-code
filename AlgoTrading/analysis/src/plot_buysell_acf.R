
# --- configurable constants

PLOTFILE <- "plot_buysell_acf.pdf"

load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
dat.all <- probe
#load(file="/home/chefele/AlgoTrading/data/training.Rsave")
#dat.all <- training

security_ids <- sort(unique(dat.all$security_id))

# --- plotting functions

plotBuySellACF <- function(in.dat, in.tag) {
    bs <- as.factor(in.dat$initiator) # (B)uy or (S)ell
    plot(acf(bs,plot=FALSE), main=in.tag)
}

# --- main()

print("Now plotting ACFs")
pdf(file=PLOTFILE)
par(mfrow=c(2,2)) # 2x2 matrix of plots 

#first do processing on ALL data
dat <-  dat.all
tag <-  paste("security_id: ALL")
print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
plotBuySellACF(dat, tag)

# now do processing on each stock individually
for(security_id in security_ids) {
    security_id.mask <- dat.all$security_id == security_id
    dat <-  dat.all[ security_id.mask ,] 
    tag <-  paste("security_id:", security_id)
    print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
    plotBuySellACF(dat, tag)
}


