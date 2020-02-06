
#!/bin/bash
while read line
do 
    echo -n $line | md5sum | awk '{print $1}' 
done 

