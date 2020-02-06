
time stdbuf -o0 python image_similarities.py `find ../data/resized.images/*_1.jpeg | sort -V` | tee image_similarities.log 

