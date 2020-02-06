
grep RESULT ${1} | awk '{print $9, $0}' | sort -nr | head --lines=25
