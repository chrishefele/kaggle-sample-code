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

   train_parsein=../../../data/training_set.tsv
   valid_parsein=../../../data/valid_set.tsv
 testing_parsein=../../../data/test_set.tsv  

  train_parseout=../../../results/CH_parseEssays.training.tsv
  valid_parseout=../../../results/CH_parseEssays.valid.tsv
testing_parseout=../../../results/CH_parseEssays.test.tsv

  train_parselog=../../../logs/CH_parseEssays.training.log
  valid_parselog=../../../logs/CH_parseEssays.valid.log
testing_parselog=../../../logs/CH_parseEssays.test.log

  train_featout=../../../features/CH_parseFeatures.training.csv
  valid_featout=../../../features/CH_parseFeatures.valid.csv
testing_featout=../../../features/CH_parseFeatures.test.csv

  train_featlog=../../../logs/CH_parseFeatures.training.log
  valid_featlog=../../../logs/CH_parseFeatures.valid.log
testing_featlog=../../../logs/CH_parseFeatures.test.log


for arg_option in "$@"
do
  case "$arg_option" in

    # note: these are very time consuming to run (~hours), so results saved/cached in the .tsv files
    trainingParse )    ./parseEssays.sh    $train_parsein     $train_parseout     $train_parselog   ;;
    validParse )       ./parseEssays.sh    $valid_parsein     $valid_parseout     $valid_parselog   ;;
    testParse )        ./parseEssays.sh    $testing_parsein   $testing_parseout   $testing_parselog ;;
    
    # note: these run quickly, and use the previously parsed results 
    trainingFeatures ) ./parseFeatures.sh  $train_parseout    $train_featout      $train_featlog    ;;
    validFeatures )    ./parseFeatures.sh  $valid_parseout    $valid_featout      $valid_featlog    ;;  
    testFeatures )     ./parseFeatures.sh  $testing_parseout  $testing_featout    $testing_featlog  ;;

    * )  echo Unknown option: "$arg_option" not processed
         ;;
  esac
done


