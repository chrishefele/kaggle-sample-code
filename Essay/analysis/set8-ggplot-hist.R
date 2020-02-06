
library(ggplot2)

pdf(file="set8-ggplot-hist.pdf")

d <- read.csv('all_features_reduced.csv')

s8 <- which(d$essay_set==8 & d$sett==1)
d8 <- d[s8,]

d8$essay_score <- d8$domain1_score

hist(d8$domain1_score,breaks=50) 
table(d8$domain1_score)

print(dim(d8))

# Draw with black outline, white fill
for(bin.width in c(1,2,5)) {

    plt <- ggplot(d8, aes(x=essay_score)) +
            geom_histogram(binwidth=bin.width, colour="black", fill="white")

    print(plt)

}

