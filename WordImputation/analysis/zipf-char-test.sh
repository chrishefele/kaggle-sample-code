cat ../download/test.txt | grep -o . | sort | uniq -c | awk '{print $2,"   ", $1}' | sort  > zipf-char-test.txt 

#cat ../download/test.txt | grep -o . | sort | uniq -c | sort -nr  > zipf-char-test.txt 

