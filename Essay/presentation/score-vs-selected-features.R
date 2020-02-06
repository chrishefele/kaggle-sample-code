# score-vs-selected-features.R
# 
# plots whisker plots of essay score vs features

library(ggplot2)
source("multiplot.R")

TRAINING_FILE <- "/home/chefele/kaggle/Essay/download/release_3/training_set_rel3.tsv"
FEATURES_FILE <- "/home/chefele/kaggle/Essay/rf/data/all_features_2012-04-03.csv"


png(bg="transparent")
# PLOT_FILE     <- "score-vs-selected-features.pdf"
# pdf(file=PLOT_FILE)



training   <- read.delim(TRAINING_FILE, quote="")
features   <- read.csv(FEATURES_FILE)
features[,"CH_entropyWords"] <- -1 * features[,"CH_entropyWords"]  # fix 

# multiplot(plotlist=plotlist, cols=2)

feature.plot <- function(feature, essay_set, xlabel, plot.title) {

    essay.score  <- training[training$essay_set == essay_set, 'domain1_score']
    feat.value   <- features[features$essay_set == essay_set, feature]
    df <- data.frame(x=factor(essay.score), y=feat.value)

    cat(plot.title, "\n")

    ylabel <- paste("Essay Score ", " (Set ", essay_set,")", sep="")

    plt <- ggplot(df, aes(x, y)) + 
           geom_boxplot() + 
           coord_flip() + 
           xlab(ylabel) +
           ylab(xlabel) + 
           ggtitle(plot.title) + 
           theme_grey(base_size = 18)

    return(plt)
}

params.list <- list(

c("CH_nwords",       5,          "Word Count",          "Score vs Word Count"),
c("CH_numUniqWords", 5,          "Unique Word Count",   "Score vs Unique Word Count"),
c("CH_avgWordLen",   5,          "Avg Word Length",     "Score vs Avg Word Length"),
c("CH_pctSpellErrs", 5,          "Spelling Errors (density)", "Score vs Spelling Errors "),
c("CH_vocabSizeEst1",5,          "Estimated Vocabulary Size", "Score vs Estimated Vocabulary Size (1)"),
c("CH_vocabSizeEst2",5,          "Estimated Vocabulary Size", "Score vs Estimated Vocabulary Size (2)"),
c("CH_gzipRatioWordShuf", 5,     "Ratio",               "Score vs gzip Size Ratio wo/w Word Shuffle"),
c("CH_entropyWords",  5,         "Entropy (nats)",      "Score vs Entropy of Word Freq Distrib"),
c("CH_parseORD44pct", 5,         "Commas (density)",    "Score vs Comma Density"),
c("CH_parseORD46pct", 5,         "Periods (density)",   "Score vs Period Density"),
c("CH_parseTreeLeafDepthMax",  5,"Max Depth",           "Score vs Parse Tree Max Depth"),
c("CH_parseTreeLeafDepthAvg",  5,"Avg Depth",           "Score vs Parse Tree Avg Depth"),
c("CH_parseVBPpct",  2,          "Verbs, non-3rd person (density)", "Score vs Non 3rd-Person Verbs"),
c("CH_parseVBZpct",  2,          "Verbs, 3rd person (density)",     "Score vs 3rd-Person Verbs"),
# essay set 2 only, verb, non-3rd person, singular, present
# essay set 2 only, verb, 3rd person, singular, present
c("CH_cohesionAdjMedian_0008", 5,"Median Cohesion btw Sentences", "Score vs Cohesion"), 
# essay sets 3 & 4
c("CH_cosinePromptEssayWordCounts",  5,  "Essay/Prompt Similarity (cosine)", "Score vs Essay/Prompt Similarity (cosine)"),
c("CH_randomNormal01",  5,       "Random", "Score vs Random Feature 1"),
c("CH_randomNormal02",  5,       "Random", "Score vs Random Feature 2")

)

for(params in params.list) {
    feature     <- params[1]
    essay_set   <- params[2]
    xlabel      <- params[3]
    plot.title  <- params[4]
    plt <- feature.plot(feature, essay_set, xlabel, plot.title)
    print(plt)
}

