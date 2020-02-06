
testing  <- read.csv("/home/chefele/AlgoTrading/download/testing.csv")
probe    <- read.csv("/home/chefele/AlgoTrading/download/Nov10/testing.csv") # a holdout set 
training <- read.csv("/home/chefele/AlgoTrading/download/Nov10/training.csv")

save(testing,  file="/home/chefele/AlgoTrading/data/testing.Rsave")
save(probe,    file="/home/chefele/AlgoTrading/data/probe.Rsave")
save(training, file="/home/chefele/AlgoTrading/data/training.Rsave")

