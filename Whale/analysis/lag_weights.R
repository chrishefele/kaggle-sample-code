library(glmnet)
library(ROCR)

TRAIN_LABELS    <- '../download/data/train.csv'
PLOT_FILE       <- 'lag_weights.pdf'
NLAGS           <- 64

calcAUC <- function(predictions, labels) {  # uses ROCR library
                pred <- prediction(predictions, labels)
                auc.tmp <- performance(pred,"auc")
                auc <- as.numeric(auc.tmp@y.values)
                return(auc)
}

plotROC<- function(predictions, labels, plot.name) {
    # ROCR functions below
    plot(
        performance( 
            prediction(predictions, labels), measure = "tpr", x.measure = "fpr" 
        ), 
        main=plot.name
    )
}

print('Reading data files')
labels <- read.csv(TRAIN_LABELS)$label
X.embed <- data.frame(embed(labels,NLAGS))
middle_lag <- NLAGS %/% 2 + 1
middle_name <- names(X.embed)[middle_lag]
print(middle_name)
Y <- X.embed[[middle_name]]
X.embed[middle_name] <- NULL

print('head of X embedded')
print(head(X.embed))
print('head of Y lag')
print(head(Y))

print('Fitting model')
X.train <- as.matrix(X.embed)
Y.train <- Y
system.time( 
    fit.train <- cv.glmnet(X.train, Y.train, type.measure="auc", family="binomial")
)

# Output various stats & plots for analysis later...
coef(fit.train)
print(fit.train)
pdf(file=PLOT_FILE)
plot(fit.train)

Y.train.predictions <- predict(fit.train, newx=X.train, type="response")
print("Original AUC")
print( calcAUC(Y.train.predictions, Y) ) 
plotROC(Y.train.predictions, Y, "ROC of logistic regression on features")
