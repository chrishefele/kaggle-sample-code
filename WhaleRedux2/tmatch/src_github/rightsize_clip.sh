
inpfile=$1
outfile=$2
pid=$$

tmpfile=`dirname ${inpfile}`/TEMP${pid}.`basename ${inpfile}`

echo ${inpfile}  " -> rightsize -> " ${outfile}

sox  ${inpfile} ${tmpfile} pad  0 4000s
sox  ${tmpfile} ${outfile} trim 0 4000s
rm   ${tmpfile}

