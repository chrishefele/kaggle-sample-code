w.in <- read.csv("weights.csv")

w <- w.in[order(w.in$reg),]

plot.min <- min(w$w1,w$w2,w$w3)
plot.max <- max(w$w1,w$w2,w$w3)

pdf("weights.pdf")
plot( log10(w$reg), w$w1, type="b", ylim=c(plot.min,plot.max), main="Regression weights vs regularization, 3 file blend")
lines(log10(w$reg), w$w2, type="b")
lines(log10(w$reg), w$w3, type="b")


