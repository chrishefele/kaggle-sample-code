
source("makeFeatures.R")
load("/home/chefele/AlgoTrading/data/probe.Rsave")

st <- system.time( features <- makeFeatures(probe) ) 
print(st)

