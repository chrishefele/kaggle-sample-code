import sys
INFINITY = sys.maxint - 1
 
class Vertex(object):
     """A vertex in a graph, using adjacency list.
 
     'edges' is a sequence or collection of tuples (edges), the first element of
     which is a name of a vertex and the second element is the distance to that vertex.
     'name' is a unique identifier for each vertex, like a city name, an integer, 
     a tuple of coordinates..."""
 
     def __init__(self, name, edges):
         self.name = name
         self.edges = edges
 
def ShortestPaths(graph, source, dest):
     """Returns the shortest distance from source to dest and a list of 
        traversed vertices, using Dijkstra's algorithm.
        Assumes the graph is connected.
     """
 
     distances = {}
     names = {}
     path = []
     for v in graph:
         distances[v.name] = INFINITY # Initialize the distances
         names[v.name] = v # Map the names to the vertices they represent
     distances[source.name] = 0 # The distance of the source to itself is 0
     dist_to_unknown = distances.copy() # Select the next vertex to explore from this dict
     last = source
     while last.name != dest.name:
         # Select the next vertex to explore, which is not yet fully explored and which 
         # minimizes the already-known distances.
         next = names[ min( [(v, k) for (k, v) in dist_to_unknown.iteritems()] )[1] ]
         for n, d in next.edges: # n is the name of an adjacent vertex, d is the distance to it
             distances[n] = min(distances[n], distances[next.name] + d)
             if n in dist_to_unknown:
                 dist_to_unknown[n] = distances[n]
         last = next
         if last.name in dist_to_unknown: # Delete the completely explored vertex
             path.append(last.name)
             del dist_to_unknown[next.name]
     # return distances[dest.name], path
     return distances
