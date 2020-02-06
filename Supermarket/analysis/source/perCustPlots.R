TRAIN_FILE <- "~/Supermarket/analysis/data/training.csv"
NPLOTS <- 25

train <- read.csv(TRAIN_FILE)
train$visit_weekday <- format(as.Date(train$visit_date),"%w")

cust_ids <- sample(unique(train$customer_id),NPLOTS)

print("Sorted spends")
for(cid in cust_ids) {
    custdat <-  train[train$customer_id == cid,] 
    plot(sort(custdat$visit_spend))
    title(sub=paste("Customer_ID:", as.character(cid)))
    print(cid)
}

print("Per Customer Spend Histograms")
for(cid in cust_ids) {
    custdat <-  train[train$customer_id == cid,] 
    hist(custdat$visit_spend)
    title(sub=paste("Customer_ID:", as.character(cid)))
    print(cid)
}

print("Per Customer Gap Histograms")
for(cid in cust_ids) {
    custdat <-  train[train$customer_id == cid,] 
    hist(diff(as.Date(custdat$visit_date)))
    title(sub=paste("Customer_ID:", as.character(cid)))
    print(cid)
}

print("Weekdays distribution per customer")
for(cid in cust_ids) {
    custdat <-  train[train$customer_id == cid,] 
    plot(table(custdat$visit_weekday),type="b")
    title(sub=paste("Customer_ID:", as.character(cid)))
    print(cid)
}

print("Per Customer Spend vs Spend-1")
for(cid in cust_ids) {
    custdat <-  train[train$customer_id == cid,] 
    lag.plot(custdat$visit_spend, do.lines=FALSE)
    title(main=paste("Customer_ID:", as.character(cid)))
    print(cid)
}

print("Per Customer Gap vs Gap-1")
for(cid in cust_ids) {
    custdat <-  train[train$customer_id == cid,] 
    gaps <- diff(as.Date(custdat$visit_date))
    lag.plot(gaps, do.lines=FALSE)
    title(sub=paste("Customer_ID:", as.character(cid)))
    print(cid)
}


print("Per Customer Gap vs Spend")
for(cid in cust_ids) {
    custdat <-  train[train$customer_id == cid,] 
    gaps <- diff(as.Date(custdat$visit_date))
    spends <- custdat$visit_spend 
    spends <- spends[1:(length(spends)-1)]
    plot(spends, gaps)
    title(sub=paste("Customer_ID:", as.character(cid)))
    print(cid)
}


print("Per Customer Avg Spend vs Gap")
for(cid in cust_ids) {
    custdat <-  train[train$customer_id == cid,] 
    gaps <- diff(as.Date(custdat$visit_date))
    spends <- custdat$visit_spend 
    spends <- spends[1:(length(spends)-1)]
    plot(tapply(spends, gaps, mean))
    title(sub=paste("Customer_ID:", as.character(cid)))
    print(cid)
}


# what % > 7days? ~10% (so 90% buy again within 7 days) 

# given weekday, spend, current inventory, last gap --> next gap   -> spend on that day 
# given weekday, spend, current inventory, last gap --> next spend -> next gap 



