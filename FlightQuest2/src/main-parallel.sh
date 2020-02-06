
# run 4 instances in parallel, for speed
for n in 1 2 3 4 
do
    stdbuf -o0 python main.py ${n} 4  > main-${n}.log  &
done

echo jobs started 

wait
cat main-?.log > main.log 

# rm main-?.log

