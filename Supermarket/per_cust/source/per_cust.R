
# define constants

SPEND_TOLERANCE <- 10 
PENNY <- 0.01
SUBMISSION_FILE <- "submission.csv"
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

stat.mode <- function(x) {
   z <- table(as.vector(x))
   return( names(z)[z==max(z)] ) # note: can return multiple days
}

geometric.mean <- function(x) { 
    exp(mean(log(x+PENNY))) 
}

mode.date <- function(x) { 
    min(WEEKDAY_TO_DATE[stat.mode(x)]) 
} 

make.predictions <- function(train) {
    next_visit_date_ints      <-  tapply( train$visitWeekday, train$customer_id, mode.date ) 
    next_visit_date           <-  as.Date( next_visit_date_ints, origin="1970-01-01" ) 
    next_visit_date_per_datum <-  next_visit_date[ as.character(train$customer_id) ]

    next_visit_weekday_per_datum <- weekdays( next_visit_date_per_datum ) 
    mask <- next_visit_weekday_per_datum == train$visitWeekday
    next_visit_spend <- tapply( train$visit_spend[mask], train$customer_id[mask], median) 
    # note: in above line, median performs better than mean or geometric.mean by 0.5%-0.7%
    next_visit_spend[ next_visit_spend<SPEND_TOLERANCE ] <- SPEND_TOLERANCE

    #print("make.predictions: next_visit_date")
    #print(next_visit_date[1:200])
    #print("make.predictions: next_visit_spend")
    #print(next_visit_spend[1:200])
    #print("make.predictions: next_visit_weekday_per_datum")
    #print(next_visit_weekday_per_datum[1:200])

    if( !identical(names(next_visit_date),names(next_visit_spend))) { stop() } 
    
    return( data.frame(customer_id=names(next_visit_date), 
                       visit_date=next_visit_date, 
                       visit_spend=next_visit_spend
                      )
    )
}

test.period  <- function(df) { df[ df$visitDate >= as.Date(TEST_START) ,] }

train.period <- function(df) { df[ df$visitDate <  as.Date(TEST_START) ,] }

exclude.holidays <- function(df) {
    non_holidays <- (df$visitDate<=as.Date("2010-11-07")) | 
                    (df$visitDate>=as.Date("2011-01-03"))
    df[non_holidays,]
}

any.in.test <- function(dates_vec) { any(dates_vec >=as.Date(TEST_START)) }

any.test.visits <- function(df) {
    # filters out ~50 training data custs that have NO visit in the test period
    cust_has_test_visit <- tapply(df$visitDate, df$customer_id, any.in.test)
    df[ cust_has_test_visit[as.character(df$customer_id)], ]  
}

make.answers <- function(df) { 
    next_visit_date_ints <- tapply(df$visitDate, df$customer_id, min)
    next_visit_date      <-  as.Date( next_visit_date_ints, origin="1970-01-01" ) 
    next_visit_date_per_datum <- next_visit_date[ as.character(df$customer_id) ] 
    mask <- next_visit_date_per_datum == df$visitDate 
    next_visit_spend <- tapply(df$visit_spend[mask], df$customer_id[mask], as.numeric)
    
    #print("make.answers: next_visit_date")
    #print(next_visit_date[1:200])
    #print("make.answers: next_visit_date_per_datum")
    #print(next_visit_date_per_datum[1:200])
    #print("make.answers: next_visit_spend")
    #print(next_visit_spend[1:200])

    if (!identical( names(next_visit_date), names(next_visit_spend) )) { stop() }

    return( data.frame(  customer_id=names(next_visit_date), 
                         visit_date=next_visit_date, 
                         visit_spend=next_visit_spend
                      )
    )
}


evaluate.predictions <- function(preds, answers) {

    date_matches <- answers$visit_date == preds$visit_date 
    pct_date_matches <- 100. * sum(date_matches)/length(date_matches)
    print(paste("%Date matches:", as.character(pct_date_matches)))

    spend_matches <- abs(answers$visit_spend - preds$visit_spend) < SPEND_TOLERANCE 
    pct_spend_matches <- 100. * sum(spend_matches)/length(spend_matches)
    print(paste("%Spend matches:", as.character(pct_spend_matches)))

    date_spend_matches <- date_matches & spend_matches
    pct_date_spend_matches <- 100. * sum(date_spend_matches)/length(date_spend_matches)
    print(paste("%Date&Spend matches:", as.character(pct_date_spend_matches)))

    return(pct_date_spend_matches)
}

main <- function() {
    # read test & train data
    # file format: # customer_id,visit_date,visit_spend # 40,2010-04-04,44.83
    print("Reading datafiles")
    test_raw  <- exclude.holidays(
                     add.dates(read.csv(paste(DATA_DIR, "test.csv",    sep="")))
                 )
    train_raw <- any.test.visits( exclude.holidays( 
                     add.dates(read.csv(paste(DATA_DIR, "training.csv",sep="")))
                 ))

    print("Computing answers")
    answers <- make.answers(test.period(train_raw))

    print("Computing predictions")
    preds   <- make.predictions(train.period(train_raw))

    print("Num & head of Predictions")
    print(nrow(preds))
    print(head(preds))
    print("Num & head of Answers")
    print(nrow(answers))
    print(head(answers))
    
    evaluate.predictions(preds, answers)

    # create submission
    print("Creating and writing submission predictions")
    preds_submission <- make.predictions(train.period(test_raw))
    write.csv(preds_submission, file=SUBMISSION_FILE, quote=FALSE, row.names=FALSE)
} 

main()
