# diffcsv.R
#
# finds differences between csv fata files
#
# usage:  cat diffcsv.R | R --vanilla --args <file1.csv> <file2.csv>

errstat <- function(x1,x2) { sqrt(sum((x1-x2)^2) / sum(x1^2)) }

FILE1 <- commandArgs(trailingOnly=TRUE)[1] 
FILE2 <- commandArgs(trailingOnly=TRUE)[2] 

f1 <- read.csv(FILE1)
f2 <- read.csv(FILE2)

names.common <- unique(c(names(f1),names(f2)))
uniq.to.f2 <- setdiff(names.common,names(f1))
uniq.to.f1 <- setdiff(names.common,names(f2))
print(paste("ColNames unique to:", FILE1,as.character(uniq.to.f1)))
print(paste("ColNames unique to:", FILE2,as.character(uniq.to.f2)))
print(paste("Common ColNames   :", as.character(names.common)))

for(colName in sort(names.common)) {
    err1 <- errstat(   f1[,colName], f2[,colName] )
    err2 <- errstat(   f2[,colName], f1[,colName] )
    print(paste(as.character(err1),as.character(err2), as.character(colName)))
}

