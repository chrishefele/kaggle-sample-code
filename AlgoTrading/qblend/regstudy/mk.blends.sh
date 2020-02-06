for reg in 1e00 1e01 1e02 1e03 1e04 1e05 1e06 1e07 1e08 1e09 1e10 1e11 1e12
do 
    ~/AlgoTrading/qblend/src/qblend blendlist.regstudy2.txt blend.reg-$reg.csv $reg | tee blend.reg-$reg.log 
done


