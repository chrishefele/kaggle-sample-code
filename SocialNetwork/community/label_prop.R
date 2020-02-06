library(igraph)

for(numV in c(1000, 10000,100000, 1000000 )) {

    print("=========== Number of Vertices =================")
    print(numV)

    G <- random.graph.game(numV, 0.02 )
    memberships <- list()

    ### label.propagation.community
    print("label.propagation.community")
    print(system.time( memberships$`Label propagation` <- label.propagation.community(G) ) )

} ### for loop


