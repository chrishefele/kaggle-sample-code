
cat('reading toys\n')
toys      <- read.csv('../download/toys_rev2.csv')

d.table <- table(toys$Duration)

sizes  <- as.integer(names(d.table))
counts <- as.integer(d.table)
work.by.size <- as.numeric(sizes * counts)
cum.work.by.size <- cumsum(work.by.size)

y <- cum.work.by.size / sum(work.by.size)

x.plot <- 1:length(y) # seq(from, to, step)
y.plot <- y[x.plot] 

cat('plotting...\n')
for(log.mode in c('xy','y','x','')) {

    plot(x.plot, y.plot,  log=log.mode, type="l", main="Cumulative work vs Toy Duration", xlab="Toy Duration")

}

cat('done.\n')

