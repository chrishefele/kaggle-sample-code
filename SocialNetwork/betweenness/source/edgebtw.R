# usage:  cat edgebtw.R | R --no-restore --no-save <BETWEENESS CUTOFF> <DIRECTED_LINKS>  | tee log.log
# BETWEENESS CUTOFF = 2 | 3 | 4  
# DIRECTED_LINKS =  TRUE or FALSE

library(igraph)
library(caTools)
EDGE_FILENAME  <- "/home/chefele/SocialNetwork/data/social_train1s_and_probe10s.csv"

args <- commandArgs()
CUTOFF_BTW     <- as.integer(args[4]) 
DIRECTED_LINKS <- as.logical(args[5])
OUTPUT_FILENAME <- paste("edgebtw", "dir", as.character(DIRECTED_LINKS), "cutoff",as.character(CUTOFF_BTW), "csv",sep=".")
print(paste("Will write results to:",OUTPUT_FILENAME))

edges <- read.csv(EDGE_FILENAME, header=FALSE)
names(edges) <- c("Vout","Vin","Prob")
g <- graph.data.frame( data.frame(edges$Vout,edges$Vin), directed=DIRECTED_LINKS )

edgelist <- get.edgelist(g)
Vouts <- edgelist[,1]
Vins  <- edgelist[,2] 

system.time( EdgeBetweenness <- edge.betweenness.estimate(g,directed=DIRECTED_LINKS,cutoff=CUTOFF_BTW) ) 
df <- data.frame(Vouts, Vins, EdgeBetweenness)
write.csv(df, file=OUTPUT_FILENAME, row.names=FALSE)

