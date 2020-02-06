results <- read.csv("results.csv")
pdf(file="results.pdf")
plot_title <- "Relative Essay Score"
boxplot( tapply( results$relative.score, results$noise.level, c ), main=plot_title, horizontal=TRUE )


