
echo Running submission.py
stdbuf -o0 python submission.py 
echo

python reformatSubmission.py blend.sub    reformat-blend-sub.csv
python reformatSubmission.py submit32.sub reformat-submit32-sub.csv
python reformatSubmission.py submit64.sub reformat-submit64-sub.csv

echo Finished

