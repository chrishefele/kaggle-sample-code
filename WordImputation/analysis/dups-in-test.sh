
python read_test.py  | sort --parallel=4 | uniq -c | awk '{print $1}' | sort -n | uniq -c 

