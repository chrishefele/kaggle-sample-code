
batches=100
# about 8 batches per hour, 100 batches/12 hours

for deltas in 10000 02000 00300 00040 00005
do
    echo `date` time java -Xmx7000M Life ${batches} ${deltas} \> Life-batches-${batches}M-deltas-${deltas}.log
                time java -Xmx7000M Life ${batches} ${deltas}  > Life-batches-${batches}M-deltas-${deltas}.log
done

