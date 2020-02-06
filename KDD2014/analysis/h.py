import hashlib

target = 'fffee68353ade53e7692b23098096683'
MAX = 1250000

for i in range(MAX):
    h = hashlib.md5(str(i)).hexdigest()
    if h == target:
        print i, h
    if i % 1000 == 0:
        print  ".", 

#print hashlib.sha256(s).hexdigest()
#print hashlib.sha512(s).hexdigest()

