
pdf(file="sets78.pdf")

d <- read.csv('/home/chefele/Dropbox/essay/features/all_features.csv')

s8 <- which(d$essay_set==8 & d$sett==1)
d8 <- d[s8,]
hist(d8$domain1_score,breaks=50) 
table(d8$domain1_score)

s7 <- which(d$essay_set==7 & d$sett==1)
d7 <- d[s7,]
table(d7$domain1_score)
