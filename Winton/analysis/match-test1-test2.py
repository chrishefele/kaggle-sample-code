
import pandas
from collections import defaultdict

TEST1_FILE      = "../download/test.csv"
TEST2_FILE      = "../download/test_2.csv"
SCALEUP         = 1000*1000*1000
FEATURE_KEY     = "Feature_2"

def ids_features(fname):
    print "reading:", fname
    csv = pandas.read_csv(fname)
    ids      =  csv["Id"].values
    print csv[FEATURE_KEY].head(10)
    raise ValueError
    features = (csv[FEATURE_KEY].values * SCALEUP).round(0).astype(int)
    return zip(ids, features)

test1_id = defaultdict(list)
for t_id, feature in ids_features(TEST1_FILE):
    print "indexing test_id:", t_id, "feature:",  feature
    test1_id[feature].append(t_id)

print "comparing test2 to test1 lines"
for t_id, feature in ids_features(TEST2_FILE):
    print "test2_id :", t_id, "feature:", feature, "matches",
    print "test1_ids:", test1_id[feature],
    if len(test1_id[feature]) > 1:
        print "******MULTIMATCH********"
    else:
        print

