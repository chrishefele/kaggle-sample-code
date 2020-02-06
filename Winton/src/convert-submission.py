import pandas
import sys
from itertools import izip
from collections import defaultdict

ID_MAPPING_FILE = "../data/test-id-mapping.csv"

_, sub1_fname, sub2_fname = sys.argv
print "Converting test1 submission [%s] to test2 submission [%s]" % (sub1_fname, sub2_fname)

mapping = pandas.read_csv(ID_MAPPING_FILE)      # Id.test1, Id.test2  (but Id is an integer)
id1_to_id2 = { id1:id2 for id1, id2 in izip(mapping["Id.test1"], mapping["Id.test2"]) }

print "reading test1 submission"
sub1 = pandas.read_csv(sub1_fname)      # Id, Predicted (but Id here is stock#_col#, e.g. 1_62)
sub2 = defaultdict(float) 
print "indexing test1 submission"
for id_col, pred in izip(sub1["Id"], sub1["Predicted"]):
    t1_id, col  = id_col.split("_")
    t1_id       = int(t1_id)
    col         = int(col)
    t2_id       = id1_to_id2[t1_id]
    sub2[(t2_id, col)] = pred

print "writing test2 submission to:", sub2_fname
fout = open(sub2_fname, "w")
fout.write("Id,Predicted\n")
for id_stock in range(1, 120000+1):
    for col in range(1, 62+1):
        pred = sub2[ (id_stock, col) ] 
        if pred == 0:
            outline = "%i_%i,%i" % (id_stock, col, 0)
        else:
            outline = "%i_%i,%f" % (id_stock, col, pred)
        fout.write(outline + "\n")
fout.close()
print "done"

