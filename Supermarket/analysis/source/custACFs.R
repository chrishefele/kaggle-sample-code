
TEST_FILE  <- "~/Supermarket/analysis/data/test.csv"

test <- read.csv(TEST_FILE)
pdf("custACFs.pdf")
cust_ids <- unique(test$customer_id)
for(cust_id in sample(cust_ids, 200)) {
    print(cust_id)
    acf( test[test$customer_id==cust_id,]$visit_spend ) 
}

