import hashlib
import time

N = 1*1000*1000
HASHMOD = N*10

hashes = {}
for n in  xrange(N):
    # h = hash(hex(n)[2:]) % HASHMOD
    h = int(hashlib.sha1(hex(n)).hexdigest(), 16) % HASHMOD
    if h in hashes:
        hashes[h].append(n)
    else:
        hashes[h]=[n]

collisions = 0
for h in sorted(hashes):
    if len(hashes[h])>1:
        # print 'hash:', h, 'n_list:', hashes[h]
        collisions += len(hashes[h]) -1 
print "collisions:", collisions, "collision_fraction:", float(collisions)/N
