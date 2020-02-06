cat stsp.log | awk '
BEGIN    { flag = 0 } 
/Purity/ { flag=1-flag }
         { if(flag==1) print $0 }
'


