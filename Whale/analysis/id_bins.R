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

pdf(file='id_bins.pdf')

num_bins_set <- c(10000,5000,2000,1000,500,200,100,50,20,10,5,2,1)

train30K    <- read.csv('../download/data/train.csv')
rownums     <- 1:nrow(train30K)

mask        <- rownums %in% sample(rownums, length(rownums) %/% 3) 
train10K    <- train30K[ mask,]
train20K    <- train30K[!mask,]

train10K$id <- 1:nrow(train10K)
train20K$id <- 1:nrow(train20K)

aucs <- c()

for(num_bins in num_bins_set) {

    train10K$id_bin <- (num_bins * (train10K$id-1))  %/%  nrow(train10K) + 1
    train20K$id_bin <- (num_bins * (train20K$id-1))  %/%  nrow(train20K) + 1
    
    id_bin_means <- tapply(train10K$label, train10K$id_bin, mean)
    train20K$id_bin_mean <- as.vector(id_bin_means[train20K$id_bin])

    cat(' num_bins: ') 
    cat( as.character(num_bins))
    cat(' AUC: ') 
    auc  <- calcAUC(train20K$id_bin_mean, train20K$label)
    aucs <- c(aucs, auc)
    cat( as.character(auc) )
    cat('\n')

    #print('TRAIN10K')
    #print(head(train10K,50))
    #print('TRAIN20K')
    #print(head(train20K,50))
    #print('')

    plotROC(train20K$id_bin_mean, train20K$label, paste(as.character(num_bins), 'file_ID bins'))
}

barplot(aucs, xlab="num_bins", ylab="AUC", main="AUC vs num_bins", names.arg=as.character(num_bins_set))

