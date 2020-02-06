for f in blend.reg*.csv 
do 
    cat ~/AlgoTrading/tools/rmse.split.noheader.R | R --vanilla --args $f | tee $f.rmsesplit
done


