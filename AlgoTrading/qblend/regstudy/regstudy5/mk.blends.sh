for reg in 1e02 2e02 5e02 1e03 2e03 5e03 1e04 2e04 5e04 1e05 2e05 5e05 1e06 2e06 5e06 1e07 2e07 5e07 1e08
do 
    ~/AlgoTrading/qblend/src/qblend blendlist.regstudy5.txt blend.reg-$reg.csv $reg | tee blend.reg-$reg.log 
done


