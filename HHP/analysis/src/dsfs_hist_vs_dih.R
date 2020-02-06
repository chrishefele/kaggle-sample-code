
DATA_PATH <- "/home/chefele/kaggle/HHP/download/HHP_release3/"

claims <- read.csv(paste(DATA_PATH,'Claims.csv',sep=''))
claims <- claims[claims$Year == 'Y1',]
mid12  <- unique(claims$MemberID[claims$DSFS=='11-12 months'])
claims <- claims[claims$MemberID %in% mid12,]
print(nrow(claims))

dih.y2   <- read.csv(paste(DATA_PATH,'DaysInHospital_Y2.csv',sep=''))
mid.dih0 <- unique(dih.y2$MemberID[ dih.y2$DaysInHospital == 0 ])
mid.dih1 <- unique(dih.y2$MemberID[ dih.y2$DaysInHospital >  0 ])
mid.all  <- unique(dih.y2$MemberID)

print(length(mid.all ))
print(length(mid.dih0))
print(length(mid.dih1))

dsfs <- claims$DSFS[claims$MemberID %in% mid.all]
tbl <- sort(table(dsfs),decreasing=TRUE)
print(tbl)
print(tbl/sum(tbl))

dsfs <- claims$DSFS[claims$MemberID %in% mid.dih0]
tbl <- sort(table(dsfs),decreasing=TRUE)
print(tbl)
print(tbl/sum(tbl))

dsfs <- claims$DSFS[claims$MemberID %in% mid.dih1]
tbl <- sort(table(dsfs),decreasing=TRUE)
print(tbl)
print(tbl/sum(tbl))


