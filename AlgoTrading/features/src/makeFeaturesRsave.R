source("makeFeatures.R")

# ~ 2 minutes
load("/home/chefele/AlgoTrading/data/testing.Rsave")
print(system.time( testing.features <- makeFeatures(testing) ))
print(system.time( save( testing.features, file="testing.features.Rsave") ))

# ~ 2 minutes
load("/home/chefele/AlgoTrading/data/probe.Rsave")
print(system.time( probe.features    <- makeFeatures(probe) ))
print(system.time( save( probe.features,    file="probe.features.Rsave") ))

# ~ 25 minutes; some swapping 
load("/home/chefele/AlgoTrading/data/training.Rsave")
print(system.time( training.features <- makeFeatures(training) ))
print(system.time( save( training.features, file="training.features.Rsave") ))

