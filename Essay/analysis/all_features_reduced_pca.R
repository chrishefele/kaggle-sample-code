
# all_features_reduced_pca.R

feats <- read.csv('all_features_reduced.csv')

pdf(file='all_features_reduced_pca.pdf')

for(essay_id in unique(feats$essay_id)) {
    print(essay_id)
    feats.eset <- feats[feats$sett==1 && feats$essay_id==essay_id,]
    feats.eset$essay_id <- NULL
    feats.eset$sett     <- NULL

    print('Doing PCA...')
    feats.pca <- prcomp(feats.eset, center=TRUE, scale=TRUE)
    print(summary(feats.pca))
    plot(feats.pca, main="Principal Components Scree of Features")
}



