###################################################################
# THIS CODE WILL STACK THE CURRENT LEADERBOARD SET WITH THE RELEASED
# SET FOR BLIND SCORING
#
# WE ONLY NEED TO RUN THIS IF THE RELEASED SET DOESN'T CONTAIN THE
# CURRENT VALIDATION SET
#
# CHECK FOR ERROR MESSAGES ABOUT DUPLICATES
#
# THE COMBINED SET SHOULD THEN BE USED FOR FEATURE CREATION 
#
###################################################################
# CHANGE HISTORY
# 4/19/2012: PB Original code
# 4/20/2012: CH changed filename paths to Linux-style for testing
# 4/20/2012: CH changed read.csv to read.delim for Linux systems
# 4/20/2012: CH fixed misplaced ) in first 'if' test after rbind 
# 4/20/2012: CH changed write.csv to write.table
###################################################################

# dropbox_root <- '~/Dropbox/essay/'
dropbox_root <- '~/Essay/stackfiles/'  # (CH) added for testing; modify this for your system

#the leaderboard and final essay files
target_file_VAL  <- paste(dropbox_root,'valid_set.tsv',sep="") # validation set
target_file_VAL1 <- paste(dropbox_root,'test_set.tsv', sep="") # test set 

#this is wherever the combined file goes
combined_file_VAL <- paste('valid+test_set.tsv',sep="")   # merged validation set

#read in the 2 files
#validation_data  <- read.csv(target_file_VAL,  header=TRUE, sep = "\t", fileEncoding="windows-1252",quote="")
#validation_data1 <- read.csv(target_file_VAL1, header=TRUE, sep = "\t", fileEncoding="windows-1252",quote="")

# NOTE: The 2 read.csv lines above did NOT work on Linux; the 2 lines did work. (CH)
validation_data  <- read.delim(target_file_VAL,  quote="") 
validation_data1 <- read.delim(target_file_VAL1, quote="") 


#check the column names are identical
if ( !identical(colnames(validation_data),colnames(validation_data1)) ){
		stop(paste('\n*Column Names DONT Match :-(\n***************************\n\n',setdiff(colnames(validation_data),colnames(validation_data1))))
	}else{
		cat("\n********************\nColumn Names Match !\n********************\n")
	}

#stack them
merged_data <- rbind(validation_data,validation_data1)

# NOTE: Added these; make sure the numbers are what you'd expect, in case of a misread due to line endings, etc. (CH)
nrow(validation_data)
nrow(validation_data1)
nrow(merged_data)

#check for duplicates
colnames(merged_data)

#if(nrow(table(merged_data$essay_id)  != nrow(merged_data))) {  # NOTE: misplaced ')'; updated line is below (CH)
if (nrow(table(merged_data$essay_id)) != nrow(merged_data) ) {
 stop(paste('\n*Duplicate Essay IDs!!!! :-(\n***************************\n\n'))
}

if (max(table(merged_data$essay_id)) > 1 ) {
 stop(paste('\n*Duplicate Essay IDs!!!! :-(\n***************************\n\n'))
}

if (max(table(merged_data$domain1_predictionid)) > 1 ) {
 stop(paste('\n*Duplicate  Prediction1  IDs!!!! :-(\n***************************\n\n'))
}

if (max(table(merged_data$domain2_predictionid)) > 1 ) {
 stop(paste('\n*Duplicate Prediction2 IDs!!!! :-(\n***************************\n\n'))
}

#write the merged file
# write.csv(write.csv(merged_data, file=combined_file_VAL, row.names = FALSE,quote = FALSE, na="")) 

# NOTE: We need a .tsv not a .csv, so an edited version of the line above using write.table is below. 
write.table(merged_data, file=combined_file_VAL, row.names=FALSE, quote=FALSE, na="", sep="\t", eol="\n")

# NOTE: BE CAREFUL ABOUT LINE ENDINGS ! eol="\r\n" below produces Windows line endings on a Unix-like OS. 

