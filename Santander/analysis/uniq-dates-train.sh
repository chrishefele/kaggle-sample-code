
TRAIN_CSV="../download/train_ver2.csv"

for col_n in 1 ; 
do
    echo ${TRAIN_CSV} ":" column ${col_n}
    csvcut -c ${col_n} ${TRAIN_CSV} | sort | uniq --count
    echo
done


