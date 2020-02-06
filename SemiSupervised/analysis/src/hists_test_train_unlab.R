ALL_ANALOGPCA <- "/home/chefele/SemiSupervised/data/data/train+test+unlabeled_analogpca.csv"

indata <- read.csv(ALL_ANALOGPCA, header=FALSE)
pcs <- indata
# pcs <- data.frame(prcomp.obj$x)
train_analogpca <- pcs[    1: 50000,]      # TODO: define constants; 1:50k is train, 50k:100k is test, rest is ulabeled 
test_analogpca  <- pcs[50001:100000,]
unlab_analogpca <- pcs[      100001:nrow(pcs),]

varnames <- names(test_analogpca)
for(name in varnames) {
    print(name)
    hist(train_analogpca[[name]])
    hist(test_analogpca[[name]])
    hist(train_analogpca[[name]])
}





