
logfile=cp_to_dropbox.log

date >> $logfile

cp --update --verbose --recursive   ../../../../final/features/*   ~/Dropbox/essay/final/features/ | tee -a $logfile
cp --update --verbose --recursive   ../../../../final/logs/*       ~/Dropbox/essay/final/logs/     | tee -a $logfile
cp --update --verbose --recursive   ../../../../final/results/*    ~/Dropbox/essay/final/results/  | tee -a $logfile
cp --update --verbose --recursive   ../../../../final/src/ch/*     ~/Dropbox/essay/final/src/ch/   | tee -a $logfile
 
echo >> $logfile

