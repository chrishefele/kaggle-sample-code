import os.path
import gensim
from nltk.corpus import brown

TRAIN_FILE = '/home/chefele/kaggle/WordImputation/download/train_v2.txt'
MODEL_FILE = 'model.mdl'

def sentence_reader():
    for line_num, line in enumerate(open(TRAIN_FILE,'r')):
        if line_num % (100*1000) == 0:
            print 'read line:', line_num
        yield line.rstrip().split()
    
#for sentence in brown.sents(): # about 50K sentences
#    yield sentence

if not os.path.isfile(MODEL_FILE):
    print "Training word2vec model"
    sentences = sentence_reader()
    model = gensim.models.Word2Vec(sentences, min_count=5)
    print "Saving word2vec model to:", MODEL_FILE
    model.save(MODEL_FILE)
else:
    print "Loading word2vec model from:", MODEL_FILE
    model = gensim.models.Word2Vec.load(MODEL_FILE)

print "Model loaded."


words = 'the and that this it'.split()
for word in words:
    print word, "->", model.most_similar(positive=[word])

print
print model.similarity('man','woman')
print model.most_similar(positive=['Washington'])
print model.most_similar(positive=['Boston'])
print model.most_similar(positive=['President', 'woman'], negative=['man'])



