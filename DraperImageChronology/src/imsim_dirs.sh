

cut -f 1 -d " " x100 > x100.f1
cut -f 2 -d " " x100 > x100.f2
cut -f 3 -d " " x100 > x100.f3

for f in `cat x100.f2`
do
    find ../download -name "$f" >> x100.f2.find
done


for f in `cat x100.f3`
do
    find ../download -name "$f" >> x100.f3.find
done

paste x100.f1 x100.f2.find x100.f3.find

rm x100.f1 x100.f2 x100.f3

