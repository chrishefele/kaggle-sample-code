
x <- read.csv('dups_train_test_map.csv')

png(file="dups_train_test_map.png")

plot(x, xlim=c(0,30000),ylim=c(0,55000),
     main="Audio File Duplicates in Both Test & Training Sets",
     xlab="Train File Index (trainXXXX.aiff)",
     ylab="Test File Index (testXXXX.aiff)"
)

