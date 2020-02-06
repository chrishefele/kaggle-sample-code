import sys

fname1 = sys.argv[1]
fname2 = sys.argv[2]


def read_edges(fname):
    tour1 = []
    tour2 = []
    edges = set()
    for line in open(fname):
        try:
            # city_id = int(line)
            city_id = int(line.split(',')[0])
        except ValueError:
            continue
        if city_id == -1:
            continue
        tour1.append(city_id)
    tour2 = tour1[1:] + tour1[:1] 
    for city1, city2 in zip(tour1, tour2):
        edges.add( (city1,city2) ) 
        edges.add( (city2,city1) ) 
    return edges

tour1_edges = read_edges(fname1)
tour2_edges = read_edges(fname2)

print "tour1_edges:", len(tour1_edges),
print "tour2_edges:", len(tour2_edges),
print "common_edges:", len(tour1_edges.intersection(tour2_edges)),
print fname1, fname2


