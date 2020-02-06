library(glmnet)
library(ROCR)

TRAIN_FILE      <- '../download/trainHistory.csv' 
TEST_FILE       <- '../download/testHistory.csv' 
PLOT_FILE       <- 'logistic.pdf'
SUBMISSION_FILE <- 'logistic.csv'

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

cat('Reading training file: ', TRAIN_FILE, '\n')
# ***********  TODO prepare the training set & labels 
# use ?model.matrix 
train.raw   <- read.csv(TRAIN_FILE)
train.dates <- as.Date(train.raw$offerdate)
mask.train.train <- train.dates > median(train.dates)
mask.train.test  <- !mask.train.train

train.fac <- data.frame(chain   = factor(train.raw$chain)
                      , offer   = factor(train.raw$offer)
                      , market  = factor(train.raw$market) 
                      , repeater= factor(train.raw$repeater)
          )

#LIMIT <-10000
#train <- model.matrix(repeater ~ ., data=train.fac[1:LIMIT,] )
#labels <- as.factor(1*(train.raw[1:LIMIT,]$repeater == "t"))
train       <- model.matrix(repeater ~ ., data=train.fac )
train.train <- train[mask.train.train,]
train.test  <- train[mask.train.test ,]

labels <- as.factor(1*(train.raw$repeater == "t"))
labels.train.train <- labels[mask.train.train]
labels.train.test  <- labels[mask.train.test ]

print(head(train.raw))
print(head(train.fac))
print(head(train.train))
print(head(train.test))
print(head(labels.train.train))
print(head(labels.train.test))
#stop()

#id,chain,offer,market,repeattrips,repeater,offerdate
#86246,205,1208251,34,5,t,2013-04-24
#12682470,18,1197502,11,0,f,2013-03-28
#13807224,4,1204576,1,0,f,2013-04-05

# ***********  END/ TODO prepare the training set & labels 

cat('Fitting model\n')
X.train <- as.matrix(train.train)
Y.train <- labels.train.train

system.time( 
   #fit.train <- cv.glmnet(X.train, Y.train, type.measure="auc", family="binomial" )
    fit.train <-    glmnet(X.train, Y.train, family="binomial" )
)

# Output various stats & plots for analysis later...
coef(fit.train)
print(fit.train)
pdf(file=PLOT_FILE)
plot(fit.train)

# Plot the ROC curve & estimate AUC against the training set 
Y.train.predictions <- predict(fit.train, newx=train.test, type="response")
auc.train <- calcAUC(Y.train.predictions, labels.train.test) 
cat("\nFull training set AUC (CV):", auc.train,"\n")
plotROC(Y.train.predictions, labels.train.test, "ROC of logistic regression on features")

# Write test set probability predictions to a file 
#   X.test <- as.matrix(test)
#   prediction <- predict( fit.train, newx=X.test, type="response")
#   submission.data <- data.frame(prediction)
#   write.csv(submission.data, file=SUBMISSION_FILE, row.names=FALSE,col.names=FALSE)


