test <-read.csv("fordTest.csv")
test$IsAlert <- 0
varnames <- names(test)

train<-read.csv("fordTrain.csv")

for(varname in varnames) {
print(varname)
plot( tapply(train[[varname]],train[["TrialID"]],mean) , main=paste("Train: ",varname) ,type="b")
plot( tapply(test[[varname]], test[[ "TrialID"]],mean) , main=paste("Test: ", varname) ,type="b")
}



