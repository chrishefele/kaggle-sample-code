# put each timestamp, bid and ask on a seperate line for easier analysis of probe set 

cat /home/chefele/AlgoTrading/download/Nov10/testing.csv | sed 's/,/ /g' | awk '
BEGIN { print "security_id,timestamp,bid,ask" } 
/:/ { 
        for(i=0;i<50;i++) 
            print $2,",", $(4*i+1+8),",", $(4*i+2+8),",", $(4*i+3+8); 
    } 
' 

# Data columns names:
#
#row_id,security_id,p_tcount,p_value,trade_vwap,trade_volume,initiator,
#transtype1,time1,bid1,ask1,
#transtype2,time2,bid2,ask2,
#...
#transtype50,time50,bid50,ask50
#


