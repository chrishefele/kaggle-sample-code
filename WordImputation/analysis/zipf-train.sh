
sed -e 's/\s/\n/g' < train.txt | sort | uniq -c | sort -nr  > zipf-train.txt 

