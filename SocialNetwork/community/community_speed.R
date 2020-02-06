library(igraph)

for(numV in c(1000, 10000,100000 )) {

    print("=========== Number of Vertices =================")
    print(numV)

    G <- random.graph.game(numV, 0.02 )
    memberships <- list()

    dummy <- function(xx) {
    ### edge.betweenness.community
    print("edge betweeness community")
    print(system.time( ebc <- edge.betweenness.community(G) ))
    mods <- sapply(0:ecount(G), function(i) {
     g2 <- delete.edges(G, ebc$removed.edges[seq(length=i)])
     cl <- clusters(g2)$membership
     modularity(G, cl)
    })
    g2 <- delete.edges(G, ebc$removed.edges[1:(which.max(mods)-1)])
    memberships$`Edge betweenness` <- clusters(g2)$membership
    }

    dummy <- function(xx) {
    ### fastgreedy.community
    print("fastgreedy.community")
    print(system.time( fc <- fastgreedy.community(G) ))
    memb <- community.to.membership(G, fc$merges,
                                   steps=which.max(fc$modularity)-1)
    memberships$`Fast greedy` <- memb$membership
    }

    ### leading.eigenvector.community
    print("leading.eigenvector.community")
    print(system.time( lec <- leading.eigenvector.community(G) ))
    memberships$`Leading eigenvector` <- lec$membership

    dummy <- function(xx) {
    ### spinglass.community
    print("spinglass.community")
    print(system.time( sc <- spinglass.community(G, spins=10) ))
    memberships$`Spinglass` <- sc$membership
    }

    dummy <- function(xx) {
    ### walktrap.community
    print("walktrap.community")
    print(system.time( wt <- walktrap.community(G, modularity=TRUE) ))
    wmemb <- community.to.membership(G, wt$merges,
                                    steps=which.max(wt$modularity)-1)
    memberships$`Walktrap` <- wmemb$membership
    }

    ### label.propagation.community
    print("label.propagation.community")
    print(system.time( memberships$`Label propagation` <- label.propagation.community(G) ) )

} ### for loop


