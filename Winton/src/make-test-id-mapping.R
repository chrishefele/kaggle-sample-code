
TEST1.FILE  <- "../data/test.RData"
TEST2.FILE  <- "../data/test_2.RData"

TEST.ID.MAPPING.FILE <- "../data/test-id-mapping.csv"

SCALE.UP    <- 1000*1000
MERGE.KEY.COLS  <- c("Ret_MinusOne", "Ret_MinusTwo")
KEEP.COLS   <- c("Id", MERGE.KEY.COLS)

getTestData <- function(fname) {
    cat("reading data from:", fname, "\n")
    test.data <- readRDS(fname)[,KEEP.COLS]
    test.data[is.na(test.data)] <- 0
    test.mergekeys <- trunc(SCALE.UP * test.data)
    test.mergekeys["Id"] <- test.data["Id"]
    return(test.mergekeys)
}

test1.df <- getTestData(TEST1.FILE)
test2.df <- getTestData(TEST2.FILE)

cat("merging\n")
test.merge <- merge(x=test1.df, y=test2.df, 
                    by=MERGE.KEY.COLS, 
                    all.x = TRUE, 
                    suffixes=c(".test1", ".test2"))

# sort by ID of test1
ordering   <- order(test.merge[,"Id.test1"])
test.merge <- test.merge[ordering,]

print(head(test.merge, 20))
print(nrow(test.merge))
print(length(unique(test.merge$Id.test1)))
print(length(unique(test.merge$Id.test2)))

cat("\nStock Ids in test1 but NOT in test2\n")
mask <- is.na(test.merge$Id.test2)
print(test.merge[mask,])


cat("\nwriting test1 Id -> test2 Id mapping file to:", TEST.ID.MAPPING.FILE, "\n")
df.out <- test.merge[,c('Id.test1','Id.test2')]
write.csv(df.out, file=TEST.ID.MAPPING.FILE, quote=FALSE, row.names=FALSE)


