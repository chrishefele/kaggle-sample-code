# examine testing timestamps by reverse engineering the testing / probe sets

# pdf(file="x")

sortBySecDayTime <- function(df) {
    d <- df[order(df$security_id, df$p_tcount, df$time1),] 
    return( data.frame( security_id=d$security_id, 
                        p_tcount=d$p_tcount,
                        time1=d$time1
            )
    )
}

load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
print(sortBySecDayTime(probe))

# load(file="/home/chefele/AlgoTrading/data/testing.Rsave")
# print(sortBySecDayTime(testing))

