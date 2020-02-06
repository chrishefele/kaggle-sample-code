for(N_CITIES in c(10000,20000,30000,40000,50000,60000,70000,80000,90000)) {

    x<-runif(N_CITIES)
    y<-runif(N_CITIES)
    df <- data.frame(x=x,y=y)
    cities <- as.matrix(df)
    print(paste("calculating dist for ", as.character(N_CITIES),"cities"))
    cities.dist <- dist(cities)
    print("Done.")

}

