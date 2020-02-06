

log1plus  <- function(x)    { log(x+1) } # convert DIH to log-domain DIH
exp1minus <- function(x)    { exp(x)-1 } # convert log-domain DIH to DIH

dih.df <- read.csv("/home/chefele/kaggle/HHP/download/HHP_release3/DaysInHospital_Y2.csv")

dih <- log1plus(dih.df$DaysInHospital)
dih.clamped <- pmax(0, pmin(1, dih))

print("Log DIH Range before clamping")
print(range(dih))
print("Log DIH Range after clamping")
print(range(dih.clamped))

err   <- dih - dih.clamped
rmsle <- sqrt(mean(err*err))
cat(paste('RMSLE vs clamped set:', as.character(rmsle), '\n'))

