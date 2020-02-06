# script to form CSV files of my features for William
# it requires the makeFeaturesRsave.R to have been run
# to create the .Rsave files of features

load("testing.features.Rsave")

write.csv(  testing.features, 
            file="testing.features.csv",        
            quote=FALSE, row.names=FALSE, col.names=TRUE
)


load("probe.features.Rsave") 
load("training.features.Rsave")

write.csv(  rbind(training.features, probe.features), 
            file="training+probe.features.csv", 
            quote=FALSE, row.names=FALSE, col.names=TRUE
)

