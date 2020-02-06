
train <- read.csv("/home/chefele/SocialNetwork/download/social_train.csv",header=FALSE)
names(train) <- c("Vout", "Vin")

sample.mask <- sample(1:nrow(train), 8960, replace=TRUE)
train.sample <- train[sample.mask,]
write.csv(train.sample, file="sample_train_list.csv", row.names=FALSE, col.names=FALSE)

unique.Vin <- unique(train$Vin)
dummy.Vout <- unique.Vin
df <- data.frame(dummy.Vout,unique.Vin)

sample.mask <- sample(1:nrow(df), 8960, replace=TRUE)
df.sample <- df[sample.mask,]
write.csv(df.sample, file="sample_train_set.csv", row.names=FALSE, col.names=FALSE)




