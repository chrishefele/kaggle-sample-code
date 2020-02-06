
pdf(file="xval-logs-plot.pdf")

df <- read.csv("xval-logs-plot.csv")

par(mfrow=c(3,4))
agg.by <- list(delta=df$delta, radius=df$radius,             nTrained=df$nTrained)  
df.agg <- aggregate(df[,"errPct"], by=agg.by, min)
for(delta.now in sort(unique(df.agg$delta))) {
    for(radius.now in sort(unique(df.agg$radius))) {
        mask.rows <- (df.agg$delta == delta.now) & (df.agg$radius == radius.now)
        xplot <- df.agg[mask.rows, "nTrained"] 
        yplot <- df.agg[mask.rows, "x"] 
        tag <- paste("delta=",as.character(delta.now)," radius=",as.character(radius.now),sep="")
        plot(xplot,yplot, type="b", xlab="nTrained", ylab="errPct", main=tag)
    }
}


agg.by <- list(delta=df$delta, radius=df$radius, reg=df$reg                      )  
df.agg <- aggregate(df[,"errPct"], by=agg.by, min)
for(delta.now in sort(unique(df.agg$delta))) {
    for(radius.now in sort(unique(df.agg$radius))) {
        mask.rows <- (df.agg$delta == delta.now) & (df.agg$radius == radius.now)
        xplot <- df.agg[mask.rows, "reg"] 
        yplot <- df.agg[mask.rows, "x"] 
        tag <- paste("delta=",as.character(delta.now)," radius=",as.character(radius.now),sep="")
        plot(as.factor(xplot),yplot, type="l", xlab="regularization", ylab="errPct", main=tag)
        # barplot(yplot, names.arg=as.character(xplot), xlab="regularization", ylab="errPct", main=tag)
    }
}


agg.by <- list(delta=df$delta, radius=df$radius                                  )
df.agg <- aggregate(df[,"errPct"], by=agg.by, min)
for(delta.now in sort(unique(df.agg$delta))) {
    mask.rows <- df.agg$delta == delta.now
    xplot <- df.agg[mask.rows, "radius"] 
    yplot <- df.agg[mask.rows, "x"] 
    tag <- paste("delta=",as.character(delta.now),sep="")
    plot(xplot,yplot, type="b", xlab="radius", ylab="errPct", main=tag)
}

