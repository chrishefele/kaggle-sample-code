
DATA_PATH <- "/home/chefele/kaggle/HHP/download/HHP_release3/"

claims <- read.csv(paste(DATA_PATH,'Claims.csv',sep=''))

dsfs <- claims$DSFS

for(yr in c('Y1','Y2','Y3')) {
    dsfs<- claims$DSFS[claims$Year==yr]

#   tbl <- sort(table(dsfs),decreasing=TRUE)
#   dsfs.dist <- tbl/sum(tbl)
#   print(yr)
#   print(dsfs.dist)
#   plot(dsfs.dist, main=paste("DSFS Distribution for",yr))

    mid12  <- unique(claims$MemberID[(claims$Year==yr) & (claims$DSFS=='11-12 months')])
    dsfs12 <- claims$DSFS[claims$MemberID %in% mid12]
    
    tbl <- sort(table(dsfs12),decreasing=TRUE)
    print(yr)
    print(length(mid12))
    print(tbl)
    print(sum(tbl))
    #dsfs12.dist <- tbl/sum(tbl)
    #print(dsfs12.dist)
    # barplot(dsfs12.dist, main=paste("DSFS12 Distribution for",yr))

}





