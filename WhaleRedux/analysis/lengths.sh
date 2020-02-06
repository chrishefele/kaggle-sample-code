ls -l ../download/test  | awk '
    BEGIN  {print "file,length"} 
    /.aif/ {print $9,",",$5}
' > lengths_test.csv


ls -l ../download/train | awk '
    BEGIN  {print "file,length"} 
    /.aif/ {print $9,",",$5}
' > lengths_train.csv

