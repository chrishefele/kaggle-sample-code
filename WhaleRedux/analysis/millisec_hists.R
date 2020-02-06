ms.all       <- read.csv('../features/filename_features_train.csv')
ms.nowhale   <- ms.all[ms.all$whale==0,]$daymsec
ms.whale     <- ms.all[ms.all$whale==1,]$daymsec

ms.nowhale100 <- ms.nowhale %% 100
ms.whale100   <- ms.whale   %% 100


png(file="millisec_hists_whale_1000.png")
hist(ms.whale, breaks=25,   
     main="Histogram of Milliseconds Field - Whale Labels",
     xlab="Milliseconds")

png(file="millisec_hists_nowhale_1000.png")
hist(ms.nowhale, breaks=25,   
     main="Histogram of Milliseconds Field - No_Whale Labels",
     xlab="Milliseconds")

png(file="millisec_hists_whale_100.png")
hist(ms.whale, breaks=1000,    xlim=range(c(100,200)),
     main="Zoomed Histogram of Milliseconds Field - Whale Labels",
     xlab="Milliseconds")

png(file="millisec_hists_nowhale_100.png")
hist(ms.nowhale, breaks=1000,  xlim=range(c(100,200)), 
     main="Zoomed Histogram of Milliseconds Field - No_Whale Labels",
     xlab="Milliseconds")



#=> filename_features_train.csv <==
#day,daymsec,daymsec_pos0,daysec,file,hour,minute,month,sec,whale,year
#28,850,0,001,20090328_000000_001s850ms_0.aif,00,00,03,00,0,2009
