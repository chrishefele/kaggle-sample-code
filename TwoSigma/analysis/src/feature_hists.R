
source("read_hdf.R")

PLOTS_FILE <- "../plots/feature_hists.pdf"
NSAMPLES <- 10000

pdf(file=PLOTS_FILE)
par(mfrow=c(2,1))

train <- read_hdf("../../download/train.h5")
train <- as.data.frame(train)
print(head(train))
print(summary(train))

for(fname in names(train)) {

    cat("plotting histogram for: ", fname,"\n")

    x <- train[,fname] 
    y <- train[,"y"]

    hist(x, 100, main=fname)

    plot.samples <- sample(1:length(x), NSAMPLES)
    plot(y[plot.samples], x[plot.samples], main=fname, type="p", pch=".")

}

cat("wrote plots to: ", PLOTS_FILE, "\n")


