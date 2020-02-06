
w.all <- read.csv('lenwhale.csv')

w.nowhale   <- w.all[w.all$whale_flag==0,]$file_length
w.whale <- w.all[w.all$whale_flag==1,]$file_length

# pdf(file="lenwhale_hists.pdf")
png(file="lenwhale_hists_whale.png")

hist(w.whale,   xlim=range(c(5000,15000)), breaks=1000,
     main="Histogram of Training File Lengths - Whale Labels",
     xlab="File length (bytes)"
    )

png(file="lenwhale_hists_nowhale.png")
hist(w.nowhale, xlim=range(c(5000,15000)), breaks=1000,
     main="Histogram of Training File Lengths - No_Whale Labels",
     xlab="File length (bytes)" 
    )


