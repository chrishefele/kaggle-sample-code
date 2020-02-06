from nltk.corpus import cmudict
d=cmudict.dict()
def nsyl(word):
    return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]]


for word in ['computer','there','animals','friendly', 'bye', 'shortbread', 'finished', 'finish', 'facebook']:
    if word in d:
        print word, nsyl(word)
    else:
        print word,'not found'


