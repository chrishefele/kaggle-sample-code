
ar <- read.csv('arrival_rate.csv')

pdf(file='arrival_rate.pdf')

plot(ar$arrival_count,   xlab = 'Day of year', ylab = 'Count of Orders (log scale)', log='y',       main='Count of Orders per Day', type='l')

plot(ar$arrival_median,  xlab = 'Day of year', ylab = 'Median Work Minutes (log scale)', log='y', main='Median Order Work-Minutes by Day', type='l')

plot(ar$arrival_minutes, xlab = 'Day of year', ylab = 'Total Work Minutes (log scale)', log='y', main='Total Work-Minutes per Day', type='l')

plot(100*cumsum(as.numeric(ar$arrival_count))/sum(as.numeric(ar$arrival_count)),   
        xlab = 'Day of year', ylab = '% of Total Orders', log='',       main='Cumulative % of Total Orders, by Day', type='l')
plot(100*cumsum(as.numeric(ar$arrival_minutes))/sum(as.numeric(ar$arrival_minutes)), 
        xlab = 'Day of year', ylab = '% of Total Work Minutes', log='', main='Cumulative % of Total Work-Minutes, by Day', type='l')

