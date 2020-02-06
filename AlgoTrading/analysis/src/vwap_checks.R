
# load the probe dataframe which contains the following columns:
# row_id,security_id,p_tcount,p_value,trade_vwap,trade_volume,initiator,transtype1,time1,bid1,ask1...

load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
sells <- probe[probe$initiator=="S",]
buys  <- probe[probe$initiator=="B",]



print(sum(buys$trade_vwap <  buys$ask46))
print(sum(buys$trade_vwap == buys$ask46))
print(sum(buys$trade_vwap >  buys$ask46))

print(sum(buys$trade_vwap <  buys$ask47))
print(sum(buys$trade_vwap == buys$ask47))
print(sum(buys$trade_vwap >  buys$ask47))

print(sum(buys$trade_vwap <  buys$ask48))
print(sum(buys$trade_vwap == buys$ask48))
print(sum(buys$trade_vwap >  buys$ask48))

print(sum(buys$trade_vwap <  buys$ask49))
print(sum(buys$trade_vwap == buys$ask49))
print(sum(buys$trade_vwap >  buys$ask49))

print(sum(buys$trade_vwap <  buys$ask50))
print(sum(buys$trade_vwap == buys$ask50))
print(sum(buys$trade_vwap >  buys$ask50))

print(sum(buys$trade_vwap <  buys$ask51))
print(sum(buys$trade_vwap == buys$ask51))
print(sum(buys$trade_vwap >  buys$ask51))

print(sum(buys$trade_vwap <  buys$ask52))
print(sum(buys$trade_vwap == buys$ask52))
print(sum(buys$trade_vwap >  buys$ask52))

print(sum(buys$trade_vwap <  buys$ask53))
print(sum(buys$trade_vwap == buys$ask53))
print(sum(buys$trade_vwap >  buys$ask53))



print(sum(buys$ask49 <   buys$ask50))
print(sum(buys$ask49 ==  buys$ask50))
print(sum(buys$ask49 >   buys$ask50))



