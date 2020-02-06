# remake.common.sh  <options...>  
#
# Using options, this remakes parse or a features file(s), for the test, training or validation sets.
# options are:  trainingParse validParse testParse  trainingFeatures validFeatures testFeatures 
#
# example:   remake.common.sh  trainingParse trainingFeatures
#
# Note:  When remaking a parse & features, parse options should appear before features 
#        e.g. do NOT do this:   remake.common.sh  trainingFeatures trainingParse 


# ------ Source data files
training=/home/chefele/Essay/download/release_3/training_set_rel3.tsv  
valid=/home/chefele/Essay/download/release_3/valid_set.tsv
#testing=  <to be provided in April> 


for arg_option in "$@"
do
  case "$arg_option" in

    # note: these are very time consuming to run (~hours), so results saved/cached in the .tsv files
    trainingParse )    ./parseEssays.sh    $training                parseEssays.training.tsv     parseEssays.training.log ;;
    validParse )       ./parseEssays.sh    $valid                   parseEssays.valid.tsv        parseEssays.valid.log ;;
    testParse )        ./parseEssays.sh    $testing                 parseEssays.test.tsv         parseEssays.test.log ;;

    # note: these run quickly, and use the previously parsed results 
    trainingFeatures ) ./parseFeatures.sh  parseEssays.training.tsv parseFeatures.training.csv   parseFeatures.training.log ;;
    validFeatures )    ./parseFeatures.sh  parseEssays.valid.tsv    parseFeatures.valid.csv      parseFeatures.valid.log ;;
    testFeatures )     ./parseFeatures.sh  parseEssays.test.tsv     parseFeatures.test.csv       parseFeatures.test.log ;;

    * )  echo Unknown option: "$arg_option" not processed
         ;;
  esac
done

