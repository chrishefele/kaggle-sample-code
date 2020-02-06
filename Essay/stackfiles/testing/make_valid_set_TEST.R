# This script creates a simulated validation/test set file 
# That file will be used to test Phil's file-stacking code.

# valid_set.tsv format is the following tab seperated cols: 
# essay_id  essay_set  essay domain1_predictionid  domain2_predictionid

valid <- read.delim("valid_set.tsv",quote="")
nrow(valid)
names(valid)

DELTA <- 100000  # just add this value to the various IDs so there's no duplicate IDs 

valid$essay_id             <- valid$essay_id             + DELTA
valid$domain1_predictionid <- valid$domain1_predictionid + DELTA
valid$domain2_predictionid <- valid$domain2_predictionid + DELTA

write.table(valid, file="valid_set_TEST.tsv", quote=FALSE, sep="\t", eol="\r\n", row.names=FALSE, na="")


