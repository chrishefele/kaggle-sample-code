library(TTR)

# whale_label   <- read.csv('../features/filename_features_train.csv')$whale
whale_label <- read.csv('../src/submission.csv')$probability

MOVAVG_N <- 1000
YLIMITS <- c(0.0,0.5)
PLOT_FILE <- 'whale_label_SMA.png'

png(filename=PLOT_FILE)

plot(   SMA(whale_label,n=MOVAVG_N), type='s', ylim=YLIMITS, 
        main='Moving Avg of Whale Label',
        xlab='Training file index',
        ylab='Moving Avg of Whale Label (N=1000)',
        col='red'
    )

whale_permute <- sample(whale_label, length(whale_label))

lines(SMA(whale_permute, n=MOVAVG_N), type='s', ylim=YLIMITS, col='blue')


legend("topleft", c('file index order','random order'), 
        cex=0.8, col=c('red','blue'),
        lty=1:3, lwd=2,bty='n')

# legend("topleft", names(autos_data), cex=0.8, col=plot_colors, lty=1:3, lwd=2, bty="n");

