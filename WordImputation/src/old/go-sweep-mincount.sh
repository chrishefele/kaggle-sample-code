
for MIN_COUNT in 8 5 3 2 
do
    ./clear-cache.sh
    time stdbuf -o0 python scoreHoldout.py ${MIN_COUNT}
done

./clear-cache.sh
