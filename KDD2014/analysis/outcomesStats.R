outcomes_file <- '../download/outcomes.csv'

cat("reading: ", outcomes_file,"\n")
outcomes <- read.csv(outcomes_file)

exciting <- 1*(outcomes$is_exciting == "t")

df <- (outcomes[,c(2:9)] == "t" )*1
last3 <- rowsumdf[,c(7:9)]
print(cor(df))
