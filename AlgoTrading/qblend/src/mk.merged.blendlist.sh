# script to create a blendlist file for the qblend blending program based on the submissions webpage on kaggle.com
# Assumes Submissions.htm was downloaded & saved, so this simple script can extract the rmses & filenames

echo reading: submissions.html
grep center                 submissions.html | sed 's/>/ /g' | sed 's/</ /g' | awk '{print $3}' > tmp.rmses
grep 'href=\"\/submissions' submissions.html | sed 's/>/ /g' | sed 's/</ /g' | awk '{print $4}' > tmp.names

paste -d, tmp.rmses tmp.names > tmp.blendlist
cat tmp.blendlist | sed 's/.gz//g' | sed 's/.zip//g' > submissions.blendlist
rm tmp.rmses tmp.names tmp.blendlist 
echo wrote: submissions.blendlist

