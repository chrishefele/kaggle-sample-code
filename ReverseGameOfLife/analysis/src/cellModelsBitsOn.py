import pickle
import cellModels
import collections 

def loadModels(filename):
    print "reading models from:", filename
    fin = open(filename, 'rb')
    models = pickle.load(fin)
    fin.close()
    print "finished reading models from:", filename
    return models


models = loadModels("model-boards-4M.pkl")

for model_id, model in enumerate(models):
    print "processing model:", model_id
    counter = collections.defaultdict(int)
    for boardHash in model.trainCounts:
        bits_on = bin(int(boardHash, 16)).count("1")
        counter[bits_on] += 1
    for bits_on in sorted(counter):
        print "bits on:", bits_on, "count:", counter[bits_on]
    print 
