
for ri in {1..7}
do
    r=`printf %02i ${ri}`
    echo stdbuf -o0 python cellModels.py ${r} \| tee cellNeighborsModel-radius-${r}.log
         stdbuf -o0 python cellModels.py ${r}  | tee cellNeighborsModel-radius-${r}.log
done

