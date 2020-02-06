
diffFiles <- function(file1, file2) {
            f1 <- read.csv(file1)
            f2 <- read.csv(file2)
            return( sum(f1-f2) ) 
}


t1 <- "/home/chefele/Dropbox/essay/submissions/FINALSUBMISIONS/CH_submit_final_test1.csv"
t2 <- "/home/chefele/Dropbox/essay/submissions/FINALSUBMISIONS/PB_submit_final_test1.csv"
t3 <- "/home/chefele/Dropbox/essay/submissions/FINALSUBMISIONS/WC_submit_final_test1.csv"

vv <- "a_valid_valid_submission.csv"

v1 <- "/home/chefele/Dropbox/essay/submissions/FINALSUBMISIONS/CH_submit_final_valid1.csv"
v2 <- "/home/chefele/Dropbox/essay/submissions/FINALSUBMISIONS/PB_submit_final_valid1.csv"
v3 <- "/home/chefele/Dropbox/essay/submissions/FINALSUBMISIONS/WC_submit_final_valid1.csv"


diffFiles(t1,t2)
diffFiles(t1,t3)
diffFiles(t2,t3)

diffFiles(vv,v1)
diffFiles(vv,v2)
diffFiles(vv,v3)

diffFiles(v1,v2)
diffFiles(v1,v3)
diffFiles(v2,v3)

