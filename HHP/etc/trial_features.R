
# Helper functions...
rmsle     <- function(p,a) { sqrt(mean((log(p+1)-log(a+1))^2)) }  #error function
log1plus  <- function(x)   { log(x+1) } # convert DIH to log-domain DIH
exp1minus <- function(x)   { exp(x)-1 } # convert log-domain DIH to DIH 

makeMonthDSFS <- function(dsfs) { 
#   Converts DSFS string to integer, e.g. "0- 1 month" -> 1
    d <- as.integer( substr( sub("-","  ",dsfs,fixed=TRUE) ,1,3) ) + 1 
    d[is.na(d)] <- 0    # default to 0 if missing 
    return(d)
}

expandVar <- function(df, dfColName) { 
#   Create binary variables from one factor (nominal) variable.
#   Args:  a dataframe (df) & factor variable namestring (dfColName)
#   Returns: Binary variables in a dataframe, one per factor level
    cat(paste("expanding:",dfColName,"\n"))
    data.frame(  
        cbind( 
            table( 1:nrow(df),
                   paste( dfColName, "__", factor(df[[dfColName]]), sep="") ))) 
}

hash_func <- function(n) { n %% 47 } 

hashExpandVar  <- function(df, dfColName) {
    df.temp <- data.frame( col.temp=hash_func(df[[dfColName]]) )
    colnames(df.temp)[1] <- dfColName
    expandVar(df.temp, dfColName)
}

sumExpandVar <- function(df, dfColName, member.ids) {
    df.expand <- expandVar(df, dfColName)
    aggregate(df.expand,by=list(Category=member.ids),FUN=sum)
}

makeGroupSums <- function(vals,grps) {
#   Return cumulative sums of data for each group (factor)
#   Args: values, and groups (factors)
#   Value: Cumulative sum vector, resets for each new group 
    gSumVecs <- tapply(vals, grps, cumsum)  # make cumulative sum vector for each group
    gSumVecsSrt <- gSumVecs[ as.character(unique(grps)) ] # reorder to orignal sorted order
    return( unlist(gSumVecsSrt) ) # flatten the list of sums into one & return 
}

# *** MAIN ***

members     <- read.csv("download/Members.csv", stringsAsFactors=FALSE)
raw.claims  <- read.csv("download/Claims.csv",  stringsAsFactors=FALSE) # test/ ???
claims <- merge(raw.claims, members, by="MemberID")

# sort claims in time-order for each member , and write it to a file
claims$MonthDSFS <- makeMonthDSFS(claims$DSFS)
claims.sorted <- claims[ order(claims$MemberID, claims$Year, claims$MonthDSFS),] 
#write.csv(claims.sorted , file="Claims.timeSorted.csv", quote=FALSE, row.names=FALSE)

# make new binary variables from claims data 
cs   <- claims.sorted
mids <- claims.sorted$MemberID

binVars <- data.frame(cbind(
    # sorting fields for timesorting claims
    #MemberID=cs$MemberID,
    #expandVar(cs,"Year"),
    #MonthDSFS=cs$MonthDSFS,

    # categorical fields, >1000 categories
    #cs$ProviderID,
    #hashExpandVar(cs,"ProviderID"),

    #cs$Vendor,
    #hashExpandVar(cs,"Vendor"),

    #cs$PCP,
    #hashExpandVar(cs,"PCP"),

    # real value(s)

    # PayDelay: don't use it. 
    # cs$PayDelay,

    # categorical vars -> binary vars 
    sumExpandVar(cs,"Specialty",        mids),
    sumExpandVar(cs,"PlaceSvc",         mids),
    sumExpandVar(cs,"LengthOfStay",     mids),
    sumExpandVar(cs,"PrimaryConditionGroup", mids),
    sumExpandVar(cs,"CharlsonIndex",    mids),
    sumExpandVar(cs,"ProcedureGroup",   mids),
    sumExpandVar(cs,"SupLOS",           mids),
    sumExpandVar(cs,"AgeAtFirstClaim",  mids),
    sumExpandVar(cs,"Sex",              mids)
))

head(binVars)
write.csv(binVars, file="Claims.newBinVars.csv", quote=FALSE, row.names=FALSE)

# TODO: 
# incorporate per-year data (DaysInHospital?)  Or ignore for now? 
# Incorporate drug and labs data? 

