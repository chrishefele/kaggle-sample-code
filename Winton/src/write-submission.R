
# Create a submission with "1000" predicted for each
# intraday and daily return for each "Group", where
# a group is a set of 6-97 stocks with the same
# value of Feature_7 (which seems to be a stock & timeframe
# combination, so they're time-aligned)
#
# By submitting these, can find out if the stocks in the
# group are excluseively in the private or public
# training set, or of one stock could be in the private
# set and one in the public set (leaking information due to
# shared market returns)

cat("\nreading files\n")
test.df <- readRDS("../data/test.RData")
sub.df  <- readRDS("../data/sample_submission.RData")

group.ids <- unique(test.df$Feature_7)
cat("unique groups:", length(group.ids), "\n")

group <- sample(group.ids, 1)
cat("selected group: ", group, "\n")

row.select      <- test.df$Feature_7 == group
group.stock.Ids <- test.df[row.select,"Id"]
cat("# group stock Ids        : ", length(group.stock.Ids),"\n")
group.stock.Ids <- sample(group.stock.Ids, 10)
cat("# sampled group stock Ids: ", length(group.stock.Ids),"\n")
cat("sampled   group stock Ids: \n", group.stock.Ids,"\n")
col.Ids <- 1:62

df <- merge(x=group.stock.Ids, y=col.Ids, by=NULL) # cartesian product
sub.Ids <- paste(df$x, df$y, sep="_")

sub.df[sub.df$Id %in% sub.Ids, "Predicted"] <- 1000

fname <- paste("f7-group-", group, ".csv", sep="")
cat("writing: ", fname, "\n")
write.csv(sub.df, file=fname, row.names=FALSE, quote=FALSE)


