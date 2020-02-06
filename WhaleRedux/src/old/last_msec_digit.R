library(TTR)
source('aucroc.R')

MOVING_AVG_LENGTH <- 1000
MOVING_AVG_LENGTH <- 100  # more optimal 

train <- read.csv('../features/filename_features_train.csv')
a <- 1- 1*(train$daymsec_pos0 == '0')
b <- 1- 1*(train$whale        == '0')

a_sma <- SMA(a, n=MOVING_AVG_LENGTH)
nowhale_mask <- a==0
a_improved <- a
a_improved[nowhale_mask] <- a_sma[nowhale_mask]

print(calcAUC(a, b))
print(calcAUC(a_sma, b))
print(calcAUC(a_improved, b))

plotROC(a, b, 'ROC for Last Digit of millisecond timestamp == 0')
print(table(a))

test <- read.csv('../features/filename_features_test.csv')
a <- 1*(test$daymsec_pos0 == '0')
print(table(a))

#==> ../features/filename_features_test.csv <==
#day,daymsec,daymsec_pos0,daysec,file,hour,minute,month,sec,whale,year
#02,300,0,40701,20090402_111500_40701s300ms.aif,11,15,04,00,-1,2009

#==> ../features/filename_features_train.csv <==
#day,daymsec,daymsec_pos0,daysec,file,hour,minute,month,sec,whale,year
#29,580,0,56787,20090329_154500_56787s580ms_0.aif,15,45,03,00,0,2009
