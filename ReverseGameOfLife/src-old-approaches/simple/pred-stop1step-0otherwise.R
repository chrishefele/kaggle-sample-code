
OUTFILE <- 'pred-stop1step-0otherwise.csv'

test    <- read.csv('../../download/test.csv')
sub     <- read.csv('../../download/sampleSubmission.csv')

startCols <- paste("start.", 1:400, sep='')
stopCols  <- paste("stop.",  1:400, sep='')

# for  1 step, use stop values    as prediction of start values
# for >1 step, use  0 (dead cell) as prediction of start values
oneStepRows <- test$delta == 1
sub[ oneStepRows, startCols] <- test[oneStepRows, stopCols]
sub[!oneStepRows, startCols] <- 0

write.csv(sub, file=OUTFILE, quote=FALSE, row.names=FALSE)


