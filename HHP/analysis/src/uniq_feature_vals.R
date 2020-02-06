y1f<-read.csv("~/kaggle/HHP/features/Y1_xfeatures.csv")
for(nm in names(y1f)) {
    v <- y1f[[nm]]
    v.binary <- sum((v>0)*1)
    cat(as.character(v.binary))
    cat(' >0_count for: ')
    cat(nm)
    cat('\t (')
    cat(as.character(length(unique(v))))
    cat(' uniqs values)\n')
}

