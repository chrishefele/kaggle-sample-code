
# NOTE: Use absolute path, without trailing slash
DIR=/home/chefele/kaggle/WordImputation

rsync  --recursive --archive --compress --verbose --progress --dry-run  ${DIR}/               chefele@otto:${DIR}

#rsync --recursive --archive --compress --verbose --progress --dry-run  ../../WordImputation/ chefele@otto:/home/chefele/kaggle/WordImputation

