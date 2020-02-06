
metrics <- read.csv("metrics.out.txt")
pdf()

edgeMask   <- metrics$EdgeProb==1
noEdgeMask <- metrics$EdgeProb==0
BARS <- 400

hist( metrics$AdamicAdar[edgeMask] , BARS)
hist( metrics$AdamicAdar[noEdgeMask],BARS )
hist( log(metrics$AdamicAdar[edgeMask]), BARS)
hist( log(metrics$AdamicAdar[noEdgeMask]), BARS)

hist( metrics$Jaccard[edgeMask],BARS)
hist( metrics$Jaccard[noEdgeMask],BARS)
hist( log(metrics$Jaccard[edgeMask]),BARS)
hist( log(metrics$Jaccard[noEdgeMask]),BARS)


hist( metrics$PrefAttachment[edgeMask],BARS)
hist( metrics$PrefAttachment[noEdgeMask],BARS)
hist( log(metrics$PrefAttachment[edgeMask]),BARS)
hist( log(metrics$PrefAttachment[noEdgeMask]),BARS)

hist( metrics$numCommonNeighbors[edgeMask],BARS)
hist( metrics$numCommonNeighbors[noEdgeMask],BARS)
hist( log(metrics$numCommonNeighbors[edgeMask]),BARS)
hist( log(metrics$numCommonNeighbors[noEdgeMask]),BARS)
 
