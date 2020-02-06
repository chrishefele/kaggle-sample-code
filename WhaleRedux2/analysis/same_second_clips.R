
diffDaysec      <- read.csv("../features/diff_daysec_features_train.csv")$diffDaysec
leakageFeatures <- read.csv("../features/leakage_features_train.csv")
clipName        <- leakageFeatures$clip
fsize           <- leakageFeatures$fsize

df <- data.frame(clip=clipName, fsize=fsize, diff=diffDaysec)

df.rotate <- rbind( df[length(df),],  df[1:length(df)-1,] ) 

df <- cbind(df,df.rotate)

print( df[df$diff==0 & df$fsize==8088,] )

