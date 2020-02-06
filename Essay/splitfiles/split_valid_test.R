
# This splits the output of Phil's code (valid+test) into seperate valid & test files
# by CH 4/25/2012

valid_template  <- read.csv("a_valid_valid_submission.csv")
valid_plus_test <- read.csv("submit__final_all1.csv")

valid_mask <- valid_plus_test$prediction_id  %in%  valid_template$prediction_id
test_mask  <- !valid_mask

valid_out <- valid_plus_test[valid_mask,]
test_out  <- valid_plus_test[test_mask, ]

write.csv(valid_out, file="CH_submit_final_valid1.csv",quote=FALSE, row.names=FALSE)
write.csv(test_out,  file="CH_submit_final_test1.csv", quote=FALSE, row.names=FALSE)


