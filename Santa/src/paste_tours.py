import pandas
import sys

fin1     = sys.argv[1]
fin1_col = sys.argv[2]
fin2     = sys.argv[3]
fin2_col = sys.argv[4]
fout     = sys.argv[5]

df = pandas.DataFrame({ 'path1':pandas.read_csv(fin1)[fin1_col], 
                        'path2':pandas.read_csv(fin2)[fin2_col] })

df.to_csv(fout, index=False)

