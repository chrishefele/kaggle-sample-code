
# driverTuning.sh -- loop over classifier parameters to find optimum 

DIR_LOGS=../tuning

for maxDepth in 02 04 06 08 12 16 24 32
do
    for maxFeatures in 10 20 30 40 50 60 70
    do
        logfile=${DIR_LOGS}/driver-feat-${maxFeatures}-depth-${maxDepth}.log
        echo `date` Starting ${logfile}
        stdbuf -o0 python driver.py  ${maxFeatures} ${maxDepth} > ${logfile}
    done
done

