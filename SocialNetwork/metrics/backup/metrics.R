#

TRAINING_DATAFILE   <- "/home/chefele/SocialNetwork/download/social_train.csv"
TEST_DATAFILE       <- "/home/chefele/SocialNetwork/download/social_test.txt"
NONEDGES_PER_EDGE   <- 1  # vary this to optimize? 
NONEDGES_SAMP_REPL  <- TRUE # non-edges sampled with replacement from all non-edges? 
DUP_SAMPLES         <- 1000000  # extra samples to make, since discard duplicate edges
RANDOM_NUM_GEN_SEED <- 1234567  

train <- read.csv(TRAINING_DATAFILE, header=FALSE)
colnames(train) <- c("Vout","Vin")
train$EdgeProb <- 1  # 1=100% probability that the edge exists

# Create tables mapping edge Vout to Vins, and edge Vin to Vouts, and vertex degrees
# (if a vertex is unused as Vin or Vout, a zero-length int (integer(0)) put in table) 
VMIN <- min(min(train$Vout),min(train$Vin)) # Max Vertex ID
VMAX <- max(max(train$Vout),max(train$Vin)) # Min Vertex ID
edgeVoutToVins <- split(train$Vin, factor(train$Vout,levels=c(VMIN:VMAX) ), drop=FALSE)
edgeVinToVouts <- split(train$Vout,factor(train$Vin ,levels=c(VMIN:VMAX) ), drop=FALSE) 
VoutDegreeOut  <- lapply(edgeVoutToVins, length) # out_degree <-VoutDegreeOut[[as.char(Vin)]]
VinDegreeIn    <- lapply(edgeVinToVouts, length) # in_degree  <-VinDegreeIn[[as.char(Vout)]]

# For training, generate a sample of "non-edges" (i.e. edge not present) 
# using randomly selected out and in vertices
numEdges <- length(train$Vout)
numNonEdgesNeeded  <- as.integer( numEdges*NONEDGES_PER_EDGE ) 
numNonEdgesSampled <- numNonEdgesNeeded + DUP_SAMPLES 
set.seed(RANDOM_NUM_GEN_SEED)
nonEdgeVout<- sample(train$Vout, numNonEdgesSampled, replace=NONEDGES_SAMP_REPL )
nonEdgeVin <- sample(train$Vin , numNonEdgesSampled, replace=NONEDGES_SAMP_REPL )
nonEdgeProb<- rep.int(0, numNonEdgesSampled) # 0=0% probability that the edge exists

# Remove any randomly-generated non-edges that already exist as edges
# (matches on a hash of in&out node IDs to uniquely identify each edge)
hashMultiplier  <- max( max(train$Vout), max(train$Vin) ) + 1 
nonEdgeHashes   <- hashMultiplier * nonEdgeVout + nonEdgeVin
edgeHashes      <- hashMultiplier * train$Vout   + train$Vin 
duplicates      <- nonEdgeHashes %in% edgeHashes
nonDupEdgesMask <- !duplicates
numDuplicates   <- sum(duplicates)
print(c("Number of duplicate nonEdges removed:",numDuplicates))
if(numDuplicates>DUP_SAMPLES) {
    print(c(numDuplicates,"nonEdge dups removed vs. ", DUP_SAMPLES,"extra edges generated"))
    stop("Could not make enough non-edge samples after duplicates removed")
}

# Put the non-edges and edges together in a single data frame for training
trainRows <- data.frame(
    Vout    = c(train$Vout,     nonEdgeVout[nonDupEdgesMask ][1:numNonEdgesNeeded]),
    Vin     = c(train$Vin,      nonEdgeVin[ nonDupEdgesMask ][1:numNonEdgesNeeded]),
    EdgeProb= c(train$EdgeProb, nonEdgeProb[ nonDupEdgesMask][1:numNonEdgesNeeded])
)

print(nrow(trainRows))

LUT <- edgeVoutToVins

Degree <- function(V1) {
    V1 <- as.character(V1)
    length(LUT[[V1]])
}

CommonNeighbors <- function(V1, V2) {
    V1 <- as.character(V1)
    V2 <- as.character(V2)
    length(intersect(LUT[[V1]],LUT[[V2]]))
}

Jaccard <- function(V1, V2) {
    V1 <- as.character(V1)
    V2 <- as.character(V2)
    length(intersect(LUT[[V1]],LUT[[V2]])) / length(union(LUT[[V1]],LUT[[V2]]))
}

PrefAttach <- function(V1, V2) {
    V1 <- as.character(V1)
    V2 <- as.character(V2)
    length(LUT[[V1]]) * length(LUT[[V2]])
}

AdamicAdar <- function(V1, V2) {
    V1 <- as.character(V1)
    V2 <- as.character(V2)
    commonNeighbors <- as.character(intersect(LUT[[V1]],LUT[[V2]]))
    sum(1.0/log(lapply( LUT[[commonNeighbors]],length )))
}

# DON'T USE MAPPLY?  JUST DO FUNCTION ON WHOLE VECTOR ????
# trainRows$DegreeIn        <- Degree, trainRows$Vin) ???????????
trainRows$DegreeOut       <- lapply( LUT[[ as.character(trainRows$Vout) ]], length)
#trainRows$DegreeOut       <- mapply(Degree, trainRows$Vout)
trainRows$CommonNeighbors <- mapply(CommonNeighbors, trainRows$Vout, trainRows$Vin)
trainRows$Jaccard         <- mapply(Jaccard,    trainRows$Vout, trainRows$Vin)
trainRows$PrefAttach      <- mapply(PrefAttach, trainRows$Vout, trainRows$Vin)
trainRows$AdamicAdar      <- mapply(AdamicAdar, trainRows$Vout, trainRows$Vin)

# Now write data to file?
# Now split into train - probe -test ? 
# test  <- read.csv(TEST_DATAFILE, header=FALSE)
# colnames(test)  <- c("Vout","Vin")



