parseHMS <- function(timeString) { strptime(timeString, format="%H:%M:%OS") }

ps <- read.csv("probe_split.csv")   # security_id, timestamp, bid, ask

times <- parseHMS(ps$timestamp)
min.times <- min(times)

ps$times <- times - min.times
ps$midpt <- (ps$bid+ps$ask)/2

ps.sec1 <- ps[ps$security_id==1 & ps$times>=10000 & ps$times <11000,]

pdf(file="probe_split.pdf")
plot(ps.sec1$times, ps.sec1$midpt, xlab="Trading day seconds", ylab="Price", main="Price vs Time, Security 1")


