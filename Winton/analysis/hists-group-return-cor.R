library(ggplot2)

ghist <- function(x1, x2, tag) {
    x1 <- c(x1) # flattens a correlation matrix 
    x2 <- c(x2)
    labels <- c(   rep("InGroup", length(x1)),
                   rep("OutGroup",length(x2)) 
               )
    df <- data.frame( x=c(x1,x2), labels=labels)
    ghist <-ggplot(df, aes(x=x, fill=labels))  +
            stat_density(   aes(y = ..density..), 
                            position = "identity", 
                            color = "black", alpha = 0.5) + 
            labs(title=tag) 
            # xlim(c(-1,1)) 
    print(ghist)
}

# --------------------------

pdf(file="hists-group-return-cor.pdf")

train <- readRDS("../data/train.RData")
train[is.na(train)] <- 0 

# --------------------------

ret.A.cols <- paste("Ret", as.character(c( 2: 60)), sep="_")
ret.B.cols <- paste("Ret", as.character(c(61:120)), sep="_")

group.keys <- train[,"Feature_7"]

for(group.key in sort(unique(group.keys))) {

    cat("processing group key: ", group.key, "\n")

    group.select <- group.key == group.keys

    ret.A            <- train[ group.select, ret.A.cols]
    ids              <- train[ group.select, "Id"] 
    row.names(ret.A) <- paste("Id_", ids, sep="")
    ret.A <- t(ret.A)
    # ret.A <- apply(ret.A, 2, cumsum) # yields prices, but inferior performance

    ret.notA            <- train[!group.select, ret.A.cols]
    ids                 <- train[!group.select, "Id"] 
    row.names(ret.notA) <- paste("Id_", ids, sep="")
    sample.rows         <- sample(1:nrow(ret.notA), nrow(ret.A))
    ret.notA <- t(ret.notA[sample.rows,])
    # ret.notA <- apply(ret.notA, 2, cumsum) # yields prices, but inferior performance

    tag <- paste("Feature_7 =", as.character(group.key))
    cors.in  <- cor(ret.A, ret.A)
    cors.out <- cor(ret.A, ret.notA) # rows=ret.A Id labels, cols=ret.notA Id labels
    ghist(cors.in, cors.out, tag)

    # is cumulative better? Test & remove if not 
    cors.in  <- rowSums(as.matrix(cors.in))
    cors.out <- rowSums(as.matrix(cors.out))
    ghist(cors.in, cors.out, tag)

    hist.diff <- cors.in - cors.out 
    ghist(hist.diff, hist.diff, tag)

}


