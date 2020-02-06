library(ROCR)

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

pdf(file='id_bins_pure.pdf')

bin_sizes <- c(1,2,3,4,5,6,8,10,15,20,50,100,200,500,1000,2000,5000,10000,30000)
aucs <- c()

for(ID_BIN_SIZE in bin_sizes) {

    train <- read.csv('../download/data/train.csv')
    train$id <- c(1:nrow(train)) 
    train$id_bin <- (train$id-1)  %/%  ID_BIN_SIZE + 1
    #print(head(train,20))

    id_bin_means <- tapply(train$label, train$id_bin, mean)
    #print(head(id_bin_means,20))

    train$id_bin_mean <- as.vector(id_bin_means[train$id_bin])
    # print(head(train,20))

    cat(' bin_size: ') 
    cat( as.character(ID_BIN_SIZE ))
    cat(' AUC: ') 
    auc <- calcAUC(train$id_bin_mean, train$label)
    aucs <- c(aucs, auc)
    cat( as.character(auc) )
    cat('\n')

    plotROC(train$id_bin_mean, train$label, paste(as.character(ID_BIN_SIZE), 'per ID bin'))
}

barplot(aucs, xlab="Bin Size", ylab="AUC", main="AUC vs ID_bin Size", names.arg=as.character(bin_sizes))

