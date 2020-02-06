
library(hexbin)
santa <- read.csv('../download/santa_cities.csv')
pdf(file='../plots/hexplot_santa_cities.pdf')
plot(hexbin(santa$x,santa$y, xbins=200))


