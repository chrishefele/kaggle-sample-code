library(glmnet)

PLOT_FILE <-  '../plots/oneDaySampleSubmissionCostAnalysis.pdf'
df <- read.csv('../data/oneDaySampleSubmissionCostAnalysis.csv')

fcost <- df$FlightCost 
df["FlightCost"]        <- NULL

df["FlightHistoryId"]   <- NULL
df["FID"]               <- NULL
df["CutoffTime"]        <- NULL
df["ArrivalAirport"]    <- NULL
df["ScheduledArrivalTime"] <- NULL

print(summary(df))

X.train <- as.matrix(df)
Y.train <- fcost

system.time( 
    fit.train <- cv.glmnet(X.train, Y.train, type.measure="mse", family="gaussian") 
)

# Output various stats & plots for analysis later...
coef(fit.train)
print(fit.train)
pdf(file=PLOT_FILE)
plot(fit.train)


