for n in 1 2 3 4 5 
do
    echo time python transitionGraphIndegrees.py ${n} ${n} \| tee transitionGraphIndegrees-${n}x${n}.log
         time python transitionGraphIndegrees.py ${n} ${n}  | tee transitionGraphIndegrees-${n}x${n}.log
done

