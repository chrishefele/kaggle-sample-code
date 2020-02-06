
load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
load(file="/home/chefele/AlgoTrading/data/testing.Rsave")
load(file="/home/chefele/AlgoTrading/data/training.Rsave") 

pdf("ratios.pdf")


probe.vwaps  <- tapply(probe$trade_vwap,    probe$security_id,      mean)
test.vwaps   <- tapply(testing$trade_vwap,  testing$security_id,    mean)
train.vwaps  <- tapply(training$trade_vwap, training$security_id,   mean)

print(probe.vwaps / test.vwaps)
hist(probe.vwaps / test.vwaps, 10)

print(probe.vwaps / train.vwaps)
hist(probe.vwaps / train.vwaps, 10)

print(test.vwaps  / train.vwaps)
hist(test.vwaps  / train.vwaps, 10)


probe.counts  <- table(probe$security_id)
test.counts   <- table(testing$security_id)
train.counts  <- table(training$security_id)

print(probe.counts / test.counts)
hist(probe.counts / test.counts,10)

print(probe.counts / train.counts)
hist(probe.counts / train.counts,10)

print(test.counts / train.counts)
hist(test.counts / train.counts,10)



print(probe.vwaps*probe.counts / (test.vwaps*test.counts))
hist( probe.vwaps*probe.counts / (test.vwaps*test.counts),10)

print(probe.vwaps*probe.counts / (train.vwaps*train.counts))
hist( probe.vwaps*probe.counts / (train.vwaps*train.counts),10)

print(test.vwaps*test.counts / (train.vwaps*train.counts))
hist( test.vwaps*test.counts / (train.vwaps*train.counts),10)


