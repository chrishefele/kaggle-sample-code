# Clear the cache when using a new MIN_COUNT for ngrams
# (or any future changes that impact the list of words that could be inserted)

echo Clearing cache files 

rm --verbose ../data/cache*.pkl

