
TEST_CSV="../download/test_ver2.csv"
TEST_CSV_SORT="../data/test_ver2.csv"

TRAIN_CSV="../download/train_ver2.csv"
TRAIN_CSV_SORT="../data/train_ver2.csv"


echo sorting ${TEST_CSV}
head -n  1 ${TEST_CSV}                                          >   ${TEST_CSV_SORT} 
tail -n +2 ${TEST_CSV}   | sort -k2,2n -k1,1 --field-separator=, >> ${TEST_CSV_SORT}
echo wrote ${TEST_CSV_SORT}

echo sorting ${TRAIN_CSV}
head -n  1 ${TRAIN_CSV}                                          >  ${TRAIN_CSV_SORT} 
tail -n +2 ${TRAIN_CSV}  | sort -k2,2n -k1,1 --field-separator=, >> ${TRAIN_CSV_SORT}
echo wrote ${TRAIN_CSV_SORT}

