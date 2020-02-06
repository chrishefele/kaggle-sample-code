
spaces <- read.csv('spaces.csv')
pdf(file='spaces.pdf')

for(eset in unique(spaces$essay_set)) {
    spaces.eset <- spaces[spaces$essay_set==eset,]
    print(eset)
    print(table(spaces.eset$count))
    plot_title <- paste('essay_set:',as.character(eset))
    plot(log(table(spaces.eset$count)),main=plot_title)
}

