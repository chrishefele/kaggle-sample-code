
TOYS_FILE  <- "../download/toys_rev2.csv"
PLOTS_FILE <- "breakpoints.pdf"

cat('Reading:', TOYS_FILE,'\n')
durations <- read.csv(TOYS_FILE)$Duration

pdf(file=PLOTS_FILE)
plot_durations <- sort(unique(as.integer(1.1^(0:114))))

for(d in plot_durations) {
    title <- paste("Toy Duration = ", as.character(d))
    x <- cumsum(durations==d)[ seq(from=1,to=length(durations), by=1000) ]
    plot(x, type='l', main=title, xlab="ToyId", ylab="Count") 
    cat(title,'\n')
}


