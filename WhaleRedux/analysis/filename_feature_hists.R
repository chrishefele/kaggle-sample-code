

pdf(file="filename_feature_hists.pdf")

train <- read.csv('../features/filename_features_train.csv')

train_whale   <- train[train$whale==1,]
train_nowhale <- train[train$whale==0,]

for(nm in names(train)) {
    cat(nm,'\n')
    if(nm=='file') next

    hist(train_whale[[  nm]], main=paste(nm, "Whale   Histogram"))
    hist(train_nowhale[[nm]], main=paste(nm, "NoWhale Histogram"))
}


# ==> filename_features_train.csv <==
# day,daymsec,daymsec_pos0,daysec,file,hour,minute,month,sec,whale,year
# 28,850,0,001,20090328_000000_001s850ms_0.aif,00,00,03,00,0,2009
# 28,100,0,010,20090328_000000_010s100ms_0.aif,00,00,03,00,0,2009

