# script to loop find optimum window size in seconds for naive predictor at market open 

ctr=0
for secs in  10  20  30  40  50  60  70  80  90 100 110 120 140 160 180 200 220 240 280 320 360 420 480 540 600 660 720 780 840 900 960 1020 1080 1140 1200
do
   echo cat mopen.naive.R \| R --vanilla --args regression.dynamics.probe.tsmooth.csv probe $secs \>  mopen.$secs.log \& 
        cat mopen.naive.R  | R --vanilla --args regression.dynamics.probe.tsmooth.csv probe $secs  >  mopen.$secs.log  & 
   ctr=`expr $ctr + 1`
   echo "secs:" $secs "counter:" $ctr
   if ((`expr $ctr % 4`==0)); then  
       echo "***** Waiting for processes to complete"
       echo `date`
       wait
       sleep 1 
   fi
done

