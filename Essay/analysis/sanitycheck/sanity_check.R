# sanity_check.R
#

sanityCheck <- function(training_filename, validation_filename, plot_filename) {

    P_VALUE_THRESHOLD <- 0.05  # p-statistic threshold; when crossed, prints a warning
                               # and plots the cumulative distributions 

    pdf(file=plot_filename)

    cat(paste("reading:",training_filename,"\n"))
    tf <- read.csv(training_filename)
    cat(paste("reading:",validation_filename,"\n"))
    vf <- read.csv(validation_filename)

    essay_sets    <- sort(intersect(unique(tf$essay_set), unique(vf$essay_set)))
    feature_names <- sort(intersect(names(tf),names(vf)))
    print(feature_names)

    for(eset in essay_sets) {
        for(feature_name in feature_names) {
            cat(paste("essay_set:", eset, "feature:", feature_name,"\n"))

            samp1 <- sort( tf[tf$essay_set==eset, feature_name])
            samp2 <- sort( vf[vf$essay_set==eset, feature_name])

            pvalue <- as.character(round(ks.test(samp1,samp2)$p.value,4))
            if(pvalue<P_VALUE_THRESHOLD) {
                warning_flag <- "*** DIFFERENT? ***"
                cat(paste("DIFFERENT?: ", "essay_set:", eset, "pvalue:", pvalue, "feature:", feature_name, "\n"))
            } else {
                warning_flag <- ""
            }

            lens1 <- (1:length(samp1)) / length(samp1)
            lens2 <- (1:length(samp2)) / length(samp2)
            plot.title <- paste(eset, feature_name, pvalue, warning_flag)
            if(pvalue<P_VALUE_THRESHOLD) {
                plot( samp1, lens1, type="l", main=plot.title, xlab="Feature Value", ylab="Cumulative Distribution")
                lines(samp2, lens2 )
            }
        }
    }
}


sanityCheck(
"/home/chefele/Essay/final/features/CH_cohesionFeatures.training.csv",
"/home/chefele/Essay/final/features/CH_cohesionFeatures.valid.csv",
"CH_cohesionFeatures.sanitycheck.pdf"
)


sanityCheck(
"/home/chefele/Essay/final/features/CH_parseFeatures.training.csv",
"/home/chefele/Essay/final/features/CH_parseFeatures.valid.csv",
"CH_parseFeatures.sanitycheck.pdf"
)

sanityCheck(
"/home/chefele/Essay/final/features/CH_xfeatures.training.csv",
"/home/chefele/Essay/final/features/CH_xfeatures.valid.csv",
"CH_xfeatures.sanitycheck.pdf"
)



