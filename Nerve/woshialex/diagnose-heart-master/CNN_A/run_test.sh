#!/bin/bash
#Test cases, no need to retrain the network
#start=501;
#end=700;
start=701;
end=1140;
for version in 3 5 6 7 10 11 12 13
do
	#set the parameters
	cp config_v"$version".py config.py
	#forecast the contours for all the cases
	./predict_net.py $start $end
done

./get_sex_age.py $start $end
