library("lsa")

tm <- textmatrix("split.out.96")
print(tm)
summary(tm)

lsaSpace <- lsa(tm, dims=dimcalc_share(share=0.7) ) 
print(lsaSpace)
summary(lsaSpace)

tmSpace <- as.textmatrix(lsaSpace)
print(tmSpace)
summary(tmSpace)

csine <- cosine(tmSpace)
print(csine)

