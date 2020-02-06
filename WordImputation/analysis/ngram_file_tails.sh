
for f in ../data/train_ngrams*
do
    echo file: $f
    echo lines: `cat $f | awk 'END {print NR}'`
    echo tail distribution
    cat $f | awk '{print $1}' | uniq -c | tail 
    echo
done

