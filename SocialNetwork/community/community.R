library(igraph)

G <- random.graph.game(100, 23.0/100)

memberships <- list()

### edge.betweenness.community
ebc <- edge.betweenness.community(G)
mods <- sapply(0:ecount(G), function(i) {
 g2 <- delete.edges(G, ebc$removed.edges[seq(length=i)])
 cl <- clusters(g2)$membership
 modularity(G, cl)
})

g2 <- delete.edges(G, ebc$removed.edges[1:(which.max(mods)-1)])
memberships$`Edge betweenness` <- clusters(g2)$membership

### fastgreedy.community
fc <- fastgreedy.community(G)
memb <- community.to.membership(G, fc$merges,
                               steps=which.max(fc$modularity)-1)
memberships$`Fast greedy` <- memb$membership

### leading.eigenvector.community
lec <- leading.eigenvector.community(G)
memberships$`Leading eigenvector` <- lec$membership

### spinglass.community
sc <- spinglass.community(G, spins=10)
memberships$`Spinglass` <- sc$membership

### walktrap.community
wt <- walktrap.community(G, modularity=TRUE)
wmemb <- community.to.membership(G, wt$merges,
                                steps=which.max(wt$modularity)-1)
memberships$`Walktrap` <- wmemb$membership

### label.propagation.community
memberships$`Label propagation` <- label.propagation.community(G)

