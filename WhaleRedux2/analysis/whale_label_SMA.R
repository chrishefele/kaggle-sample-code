library(TTR)

TEST <-'~/kaggle/WhaleRedux2/nmkridler/submissions/WR2-useOrderingFalse/reformat-blend-sub.csv'
TEST <-'~/kaggle/WhaleRedux2/nmkridler/submissions/WR2-useOrderingFalse-shift/reformat-blend-sub.csv'
TRAIN<-'~/kaggle/WhaleRedux2/nmkridler/data_WhaleRedux2/train.csv'

PLOT_FILE <- 'whale_label_SMA.png'
MOVAVG_N  <- 1000
YLIMITS   <- c(0.0,0.8)

answers.test  <- read.csv(TEST)$probability
answers.train <- read.csv(TRAIN)$label

whale_label <- answers.test
#whale_label <- answers.train 

png(filename=PLOT_FILE)
plot(   SMA(whale_label,n=MOVAVG_N), type='s', ylim=YLIMITS, 
        main='Moving Avg of Whale Label',
        xlab='File index',
        ylab='Moving Avg of Whale Label (N=1000)',
        col='red'
    )

whale_permute <- sample(whale_label, length(whale_label))

lines(SMA(whale_permute, n=MOVAVG_N), type='s', ylim=YLIMITS, col='blue')
legend("topleft", c('file index order','random order'), 
        cex=0.8, col=c('red','blue'),
        lty=1:3, lwd=2,bty='n')

cat('Wrote PNG plot to:', PLOT_FILE,'\n')
