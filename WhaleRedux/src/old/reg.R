
train <- read.csv('../features/filename_features_train.csv')

print(tapply(train$day, train$whale, mean))
print(tapply(train$daymsec, train$whale, mean))
print(tapply(train$daymsec_pos0, train$whale, mean))
print(tapply(train$daysec, train$whale, mean))
print(tapply(train$hour, train$whale, mean))
print(tapply(train$minute, train$whale, mean))
print(tapply(train$month, train$whale, mean))
print(tapply(train$sec, train$whale, mean))
print(tapply(train$whale, train$whale, mean))
print(tapply(train$year, train$whale, mean))


# day,daymsec,daymsec_pos0,daysec,file,hour,minute,month,sec,whale,year
# 28,850,0,001,20090328_000000_001s850ms_0.aif,00,00,03,00,0,2009
