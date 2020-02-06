# make polynomial functions of the assembled feature data (e.g. f(x)=x + x^2 + x^3

TRAINING_FILE       <- "/home/chefele/Ford/blendall/fordTrain.assembled.features.csv"
TEST_FILE           <- "/home/chefele/Ford/blendall/fordTest.assembled.features.csv"

df.power <- function(df.in) {
    df.out <- data.frame( dummy=1:nrow(df.in) )
    df.out$dummy <- NULL
    for(var.name in names(df.in)) {
        print(paste("Processing:",var.name))
        if(var.name %in% c("TrialID","ObsNum","IsAlert","IsSpikeTrial","TrialFirst100")) {
            df.out[[var.name]] <- df.in[[var.name]]
        } else {
            for(pwr in 1:3) {
                out.var.name <- paste( var.name, "_power_", as.character(pwr),sep="")
                x <- df.in[[var.name]]
                df.out[[out.var.name]] <- ( ecdf(x)(x) )^pwr   # ******** percentiles 
                # df.out[[out.var.name]] <- x ^ pwr                # ******** raw data
            }
        }
    }
    return(df.out)
}

train <- read.csv(TRAINING_FILE)
test  <- read.csv(TEST_FILE)

train.out <- df.power(train)  
test.out  <- df.power(test)

write.csv(train.out,file="fordTrain.poly.csv", quote=FALSE,row.names=FALSE)
write.csv(test.out, file="fordTest.poly.csv",  quote=FALSE,row.names=FALSE)


