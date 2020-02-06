
cat('reading toys\n')
toys      <- read.csv('../download/toys_rev2.csv')

y <- cumsum(durations) / sum(durations)
x.plot <- seq(1,length(y),1000)
y.plot <- y[x.plot] 

cat('plotting...\n')
plot(x.plot, y.plot,  log='xy', type="l")
plot(x.plot, y.plot,  log='y',  type="l")
plot(x.plot, y.plot,  log='x',  type="l")
plot(x.plot, y.plot,  log='',   type="l")

cat('done.\n')

