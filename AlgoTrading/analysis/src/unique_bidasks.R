load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
dat <- probe

pre.tperiods    <- 1:50
post.tperiods   <- 51:100
nuniqs          <- function(z) { length(unique(z))   }
row.nuniqs      <- function(x) { apply(x, 1, nuniqs) } 
mk.col.names    <- function(tag, periods) { paste(tag, as.character(periods), sep="") }
bidask.nuniqs <- function(in.dat, tperiods, tag.bidask) {
    col.tags <- mk.col.names(tag.bidask, tperiods)
    vals <- cbind(in.dat[,col.tags])
    return( row.nuniqs(vals) ) 
}

pdf(file="unique_bidasks.pdf")
par(mfrow=c(2,2))

hist( bidask.nuniqs(dat,1:50,  "ask" ),  100,  main="Hist N Unique Asks T1..T50"  )
hist( bidask.nuniqs(dat,1:50,  "bid" ),  100,  main="Hist N Unique Bids T1..T50"  )
hist( bidask.nuniqs(dat,51:100,"ask" ),  100,  main="Hist N Unique Asks T51..T100")
hist( bidask.nuniqs(dat,51:100,"bid" ),  100,  main="Hist N Unique Bids T51..T100")

pre.a  <- table( bidask.nuniqs(dat,1:50,  "ask" )) 
pre.b  <- table( bidask.nuniqs(dat,1:50,  "bid" ))
post.a <- table( bidask.nuniqs(dat,51:100,"ask" ))
post.b <- table( bidask.nuniqs(dat,51:100,"bid" ))

pre.a <- pre.a / sum(pre.a)
pre.b <- pre.b / sum(pre.b)
post.a <- post.a / sum(post.a)
post.b <- post.b / sum(post.b)

print(pre.a)
print(pre.b)
print(post.a)
print(post.b)

plot( pre.a,  main="Hist N Unique Asks T1..T50"  )
plot( pre.b,  main="Hist N Unique Bids T1..T50"  )
plot( post.a, main="Hist N Unique Asks T51..T100" )
plot( post.b, main="Hist N Unique Bids T51..T100" )

# print correlations between num of unique bid(ask) prices before vs after the event 
print(cor( bidask.nuniqs(dat,1:50,"ask" ), bidask.nuniqs(dat,51:100,"ask" )))
print(cor( bidask.nuniqs(dat,1:50,"bid" ), bidask.nuniqs(dat,51:100,"bid" )))


