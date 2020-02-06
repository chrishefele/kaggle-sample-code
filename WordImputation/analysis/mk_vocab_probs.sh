
cat ../data/train_ngrams_1+1.txt | awk '{sum+=$1; print NR, sum/761000000, $0}' > ../analysis/vocab_probs.txt

