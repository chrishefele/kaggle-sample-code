
TRAIN_FILE <- "~/Supermarket/analysis/data/training.csv"
train <- read.csv(TRAIN_FILE)

train$visitDate <- as.Date(train$visit_date)

avgVisitGap <- function(x) { 1.0 * as.integer(max(x)-min(x)) / length(x) }

visit.gaps <- tapply(train$visitDate, train$customer_id, avgVisitGap )

pdf("custVisitGaps.pdf")

hist(log10(visit.gaps))
hist(log10(visit.gaps), 200)

hist(visit.gaps)
hist(visit.gaps, 200)

weekgaps <- sum(visit.gaps>=7) / sum(visit.gaps>=0)

print(weekgaps)

