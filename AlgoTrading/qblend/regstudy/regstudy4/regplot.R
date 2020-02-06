x <- read.csv("regstudy4.csv",header=FALSE)
x$V1 <- NULL
x$V2 <- NULL
x$V4 <- NULL

regs <- x$V3

pdf("regstudy4.pdf")

plot(log10(regs), x$V3, type="b", ylim=c(-1,1))
for(nm in names(x)) { 
    lines(log10(regs), x[[nm]], type="b")
}


plot(log10(regs), x$V3, type="l", ylim=c(-1,1))
for(nm in names(x)) { 
    lines(log10(regs), x[[nm]], type="l")
}


for(nm in names(x)) { 
    plot(log10(regs), x[[nm]], type="b", main=nm, ylim=c(-1,1))
}



