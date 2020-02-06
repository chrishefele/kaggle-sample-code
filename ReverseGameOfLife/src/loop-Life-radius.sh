
# batches=32
batches=1

# for radius in 0.0 0.9 1.1 1.5 2.1 2.3 2.9 3.1 3.2 3.7 4.1 4.2 4.5 
for radius in 0.0 0.9 1.1 1.5 2.1 2.3 2.9 3.1 3.2 3.7 4.1 4.2 4.5 
do
    echo `date` time java -Xmx7000M Life ${batches} ${radius} \> Life-radius-${radius}-boards-${batches}M.log
                time java -Xmx7000M Life ${batches} ${radius}  > Life-radius-${radius}-boards-${batches}M.log
done

