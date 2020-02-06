CLAIMS_FILE <- "/home/chefele/HHP/download/HHP_release3/Claims.csv"

claims <- read.csv(CLAIMS_FILE)

length(unique(claims$ProviderID))
length(unique(claims$Vendor))
length(unique(claims$PCP))

tpid  <- table(claims$ProviderID)
tvnd  <- table(claims$Vendor)
tpcp  <- table(claims$PCP)

cumsum(sort(tpid, decreasing=TRUE)/sum(tpid))
cumsum(sort(tvnd, decreasing=TRUE)/sum(tvnd))
cumsum(sort(tpcp, decreasing=TRUE)/sum(tpcp))

sort(tpid, decreasing=TRUE)
sort(tvnd, decreasing=TRUE)
sort(tpcp, decreasing=TRUE)

