
echo running genTrainMetrics
stdbuf -o0 python genTrainMetrics.py
echo

echo running genTestMetrics
stdbuf -o0 python genTestMetrics.py
echo

echo running ordering
stdbuf -o0 python ordering.py
echo

echo running driver
stdbuf -o0 python driver.py 
echo

# echo running submission 
# stdbuf -o0 python submission.py 
# echo

echo
echo Finished Dont forget to run submission and reformatSubmission 
echo

