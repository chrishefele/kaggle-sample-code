library("quantreg")
library("reshape2")
library("dplyr")
library("glmnet")
library("methods")

TRAIN.FILE <- "../data/train.RData"

PLOT.FILE  <- "train-models.pdf"
pdf(file=PLOT.FILE) 
# par(mfrow=c(2,2))

errs.glmnet <- 0
errs.zero   <- 0

main <- function() {

    train <- tbl_df(readRDS(TRAIN.FILE))
    train[is.na(train)] <- 0 

    for(row.n in 1:nrow(train)) {

        row.dat     <-   train[row.n,]
        row.Id      <-   as.integer(row.dat$Id)
        row.group   <-   as.integer(row.dat$Feature_7)
        returns.Id  <-   select(row.dat, Ret_2:Ret_121)
        returns.group <- train %>% 
                         #filter(Feature_7 == row.group) %>%  # RESTORE AFTER TESTING 
                         filter(Id == row.Id) %>%             # REMOVE  AFTER TESTING
                         select(Id, Ret_2:Ret_121)

        row.names(returns.group) <- paste("Id", returns.group$Id, sep="_")
        returns.group$Id <- NULL

        X  <- t(returns.group) # USE AFTER TESTING
        #X  <- t(returns.group)[,1:3] # *** ONLY FOR TESTING
        Y  <- t(returns.Id)

        dX <- diff(X) 
        colnames(dX) <- paste("diff", colnames(dX), sep="_")
        X <- cbind( X[-1,], dX ) 
        Y <- Y[-1,]

        # now time-align Y (1 period ahead) with X variables 
        X <- X[-nrow(X), ] # skip last row
        Y <- Y[-1]         # skip first row

        X.df <- as.data.frame(X)
        #cat("\n")
        #print(head(Y))
        #print(head(X[ ,1:6]))
        #print(tail(Y))
        #print(tail(X[ ,1:6]))

        model <- cv.glmnet(X, Y, type.measure="mse", family="gaussian") # type.measure="mae"|"mse" 
        print(model)

        cat("\nrow: ", row.n, "\n")
        print(coef(model))
        plot(model)

        #curr.mae.glmnet <- mean(abs(Y - predict(model, newx=X)))
        curr.mae.glmnet <- mean(abs(Y - median(Y)))  # TODO REMOVE AFTER TESTING 
        curr.mae.zero   <- mean(abs(Y - 0))

        errs.glmnet <- errs.glmnet + curr.mae.glmnet 
        errs.zero   <- errs.zero   + curr.mae.zero 

        mae.glmnet <- errs.glmnet/row.n
        mae.zero   <- errs.zero  /row.n

        cat("----------------------------------\n")
        cat("row: ", row.n)
        cat(" curr_MAE_glmnet: ", curr.mae.glmnet)
        cat(" curr_MAE_zero: ",   curr.mae.zero)
        cat(" cur_glmnet/zero: ", curr.mae.glmnet/curr.mae.zero)
        cat(" MAE_glmnet: ", mae.glmnet)
        cat(" MAE_zero: ",   mae.zero)
        cat(" glmnet/zero: ", mae.glmnet/mae.zero, "\n")
        cat("----------------------------------\n")

        # if(row.n %% 100 == 0) cat(row.n,"\n")
        # TODO 
        # create r(t), r(t-1) for regression
        # do single-stock  regression
        # do group  regression
        # tabulate errors vs 0
    }
}

main()
       
# TRAIN columns
#Id,
#Feature_X, X=1...25
#Ret_MinusTwo, Ret_MinusOne,
#Ret_N, N=2...180
#Ret_PlusOne, Ret_PlusTwo,
#Weight_Intraday, Weight_Daily

