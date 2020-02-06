grep delta *.log | sed 's/radius/radius /g' | sed 's/delta/ delta/g' | sed 's/.log/ .log/g' > errors.txt 

