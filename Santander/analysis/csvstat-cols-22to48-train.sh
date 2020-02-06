
TRAIN_CSV="../download/train_ver2.csv"
END=48

for col_n in $(seq 22 $END);
do
    echo ${TRAIN_CSV} ":" column ${col_n}
    csvcut -c ${col_n} ${TRAIN_CSV} | csvstat
    echo
done


