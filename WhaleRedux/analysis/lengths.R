
lengths_test  <- read.csv('lengths_test.csv' )$length
lengths_train <- read.csv('lengths_train.csv')$length

print(length(lengths_test))
print(length(lengths_train))

print(length(unique(lengths_test)))
print(length(unique(lengths_train)))

print(length(intersect(unique(lengths_test),unique(lengths_train))))


