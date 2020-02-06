
for f in train*.aiff
do
    nz_file=noisered-${f}
    nz_pct=0.l
    sox ${f} -n trim 1.5 0.5 noiseprof | sox ${f} ${nz_file} noisered ${nz_pt}

    sox ${nz_file} -n spectrogram  -x 257 -y 257 -o ${nz_file}.png
    sox ${f}       -n spectrogram  -x 257 -y 257 -o ${f}.png

done

