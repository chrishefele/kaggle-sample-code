
SRC_TRAIN=../workspace/metrics-no-shift/trainMetrics.csv 
SRC_TEST=../workspace/metrics-no-shift/testMetrics.csv  

DST_TRAIN=../workspace/metrics-shift/trainMetrics.csv 
DST_TEST=../workspace/metrics-shift/testMetrics.csv  

stdbuf -o0 python shiftMetrics.py ${SRC_TRAIN} ${DST_TRAIN}
stdbuf -o0 python shiftMetrics.py ${SRC_TEST}  ${DST_TEST}

