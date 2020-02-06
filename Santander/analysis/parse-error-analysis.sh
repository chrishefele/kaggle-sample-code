
TRAIN_CSV="../download/train_ver2.csv"
TEST_CSV="../download/test_ver2.csv"

echo
echo ${TEST_CSV}
csvcut -c ult_fec_cli_1t ${TEST_CSV}  | sort | uniq -c 
echo ENDEND

echo
echo ${TRAIN_CSV}
csvcut -c ult_fec_cli_1t ${TRAIN_CSV} | sort | uniq -c 
echo ENDEND

echo
echo ${TEST_CSV}
csvcut -c indrel_1mes    ${TEST_CSV}  | sort | uniq -c 
echo ENDEND

echo
echo ${TRAIN_CSV}
csvcut -c indrel_1mes    ${TRAIN_CSV} | sort | uniq -c 
echo ENDEND


