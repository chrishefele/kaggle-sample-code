echo Remaking the feature file AND plots

./xfeatures.sh

echo Making plots

./features_plot.sh  xfeatures.training.csv  xfeatures.training.plot.pdf

