
TEST_START <- "2011-04-01"
DATA_DIR <- "/home/chefele/Supermarket/download/"

WEEKDAY_TO_DATE <- seq(as.Date(TEST_START), as.Date(TEST_START)+6, 1)
names(WEEKDAY_TO_DATE) <- weekdays(WEEKDAY_TO_DATE)

add.dates <- function(df_in) {
    df_out <- df_in 
    df_out$visitDate    <- as.Date( df_out$visit_date)
    df_out$visitWeekday <- weekdays(df_out$visitDate)
    return(df_out)
}

test.period.filter  <- function(df) { df[ df$visitDate >= as.Date(TEST_START) ,] }

train.period.filter <- function(df) { df[ df$visitDate <  as.Date(TEST_START) ,] }

exclude.holidays.filter <- function(df) {
    non_holidays <- (df$visitDate<=as.Date("2010-11-07")) | 
                    (df$visitDate>=as.Date("2011-01-03"))
    df[non_holidays,]
}

any.in.test <- function(dates_vec) { any(dates_vec >=as.Date(TEST_START)) }

any.test.visits.filter <- function(df) {
    # filters out ~50 training data custs that have NO visit in the test period
    cust_has_test_visit <- tapply(df$visitDate, df$customer_id, any.in.test)
    df[ cust_has_test_visit[as.character(df$customer_id)], ]  
}

cust2.filter <- function(df) { 
    df[df$customer_id=="2",] 
}

main <- function() {
    # read test & train data
    # file format: # customer_id,visit_date,visit_spend # 40,2010-04-04,44.83
    print("Reading datafiles")
    train_raw <- read.csv(paste(DATA_DIR, "training.csv",sep=""))
    train <- any.test.visits.filter(add.dates(train_raw))
    write.csv( test.period.filter( cust2.filter(train)),file="c2test.csv", quote=FALSE,row.names=FALSE )
    write.csv( train.period.filter(cust2.filter(train)),file="c2train.csv",quote=FALSE,row.names=FALSE )
} 

main()
