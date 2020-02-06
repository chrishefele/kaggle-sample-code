v1 <- read.csv("CH_cohesionFeatures.valid_1.csv")
v2 <- read.csv("CH_cohesionFeatures.valid_2.csv")
vt <- read.csv("CH_cohesionFeatures.valid_test.csv")

vt1  <- vt[vt$essay_id %in% v1$essay_id,]
vt2  <- vt[vt$essay_id %in% v2$essay_id,]

sqerr <- function(x,y) { sum((x-y)*(x-y)) / sum(x*x) }

sqerr(v1,v1)
sqerr(v2,v2)

sqerr(v1,v2)

sqerr(v1,vt1)
sqerr(v2,vt2)

sqerr(v1,vt2)
sqerr(v2,vt1)

print(names(vt))



