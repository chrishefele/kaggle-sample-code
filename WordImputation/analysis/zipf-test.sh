
sed -e 's/\s/\n/g' < test.txt | sort | uniq -c | sort -nr  > zipf-test.txt 

