
w <- read.csv('lenwhale.csv')

wt <- table(w$file_length, w$whale_flag)

wt.df <- data.frame(wt)
print(head(wt.df))

#file_length, whale_flag
#1166 , 0
#1714 , 1

