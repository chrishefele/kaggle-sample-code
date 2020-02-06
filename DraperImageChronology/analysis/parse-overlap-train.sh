
for i in 1 2 3 4 5
do
    for j in 1 2 3 4 5
    do
        echo
        echo ------------------- $i $j --------------------
        cat overlap-train.log | awk '{print $12, $0}' | grep "templ: $i subj: $j" | sort -n
        echo
        echo
    done
done

