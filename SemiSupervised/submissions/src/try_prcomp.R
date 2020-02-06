
DATAFILE <- "/home/chefele/SemiSupervised/data/data/train+test+unlabeled_analogpca.csv"
indata <- read.csv(DATAFILE, header=FALSE)
names(indata) <- paste("analogpca_",names(indata),sep="")
prcomp.obj  <- prcomp( indata, scale=TRUE)
pcs <- data.frame(prcomp.obj$x)

head(pcs)
nrow(pcs)
ncol(pcs)
dim(pcs)


