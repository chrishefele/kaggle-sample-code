from syntheticBoards import readTrainBoards
import sys

BOARD_SIDE = 20
BOARD_CELLS = BOARD_SIDE * BOARD_SIDE

nboards = int(sys.argv[1])
outfile = sys.argv[2]

print "writing", nboards, "training boards to:", outfile

cols = ["id","delta"]
cols.extend(["start."+str(i) for i in range(1,BOARD_CELLS+1)])
cols.extend(["stop." +str(i) for i in range(1,BOARD_CELLS+1)])
header = ','.join(cols)

fout = open(outfile,"w")
fout.write(header + "\n")

for row_id, delta, startBoard, stopBoard in readTrainBoards(nboards):
    row = [row_id, delta]
    row.extend(1*startBoard.flatten(order='F'))
    row.extend(1* stopBoard.flatten(order='F'))
    row_str = ','.join([str(x) for x in row])
    fout.write(row_str+"\n")
    if row_id % 100 == 0:
        print row_id,
        sys.stdout.flush()

print "\ndone"
