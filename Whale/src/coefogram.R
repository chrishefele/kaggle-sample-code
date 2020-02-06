
COEFS <- 'chirp.csv'
PLOT_FILE <-  'coefogram.pdf'

cat('\n*** generating coef-o-gram ***\n')

coefs <- read.csv(COEFS)$coef
print(head(coefs))

image(matrix(coefs,30,30), main='logistic regression chirp coefs')

