
TRAIN = "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
TEST  = "/home/chefele/Essay/final/data/valid+test_set.tsv"

fnames = [TRAIN, TEST]

essay_to_ids = {}
for fname in [TRAIN,TEST]:
    print "\nParsing essay file:", fname
    fin = open(fname,'r')
    header = fin.readline().split('\t')
    for line in fin:
        fields = line.split('\t')
        essay_id, essay_set, essay_raw = int(fields[0]), int(fields[1]), fields[2]
        rest = fields[3:]
        if essay_raw not in essay_to_ids:
            essay_to_ids[essay_raw] = []
        #essay_to_ids[essay_raw].append(fname+":"+str(essay_id))
        essay_to_ids[essay_raw].append(essay_id)
        if essay_id % 100 == 0:
            print essay_id,
    fin.close()
    print

print "Duplicate essays:"
for e in essay_to_ids:
    if len(essay_to_ids[e])>1:
        print essay_to_ids[e]

