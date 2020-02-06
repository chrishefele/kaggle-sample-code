require(stringr)
require(tm) # http://cran.r-project.org/web/packages/tm/tm.pdf
require(topicmodels) # http://cran.r-project.org/web/packages/topicmodels/topicmodels.pdf
require(RTextTools)
require(tm.lexicon.GeneralInquirer)
require(lda)


#set working directory
#setwd("C:/Users/Eu/Documents/ASAP Comp/data")
setwd("C:/Users/Eu/Dropbox/essay/final")

data <- read.delim ("data/training_set.tsv", header = T, quote = "")
valid <- read.delim ("data/valid_set.tsv", header = T, quote = "")


#####################################
# Function to remove  annonymisation
#####################################
 
word.list <- function(sentence) {
 
        # clean up sentences with R's regex-driven global substitute, gsub(): 
        # http://stat.ethz.ch/R-manual/R-patched/library/base/html/regex.html
        sentence = gsub('[[:punct:]]', ' ', sentence)
        sentence = gsub('[[:cntrl:]]', ' ', sentence)
        sentence = gsub("CAPS1", ' ', sentence)
        sentence = gsub("CAPS10", ' ', sentence)
        sentence = gsub("CAPS11", ' ', sentence)
        sentence = gsub("CAPS12", ' ', sentence)
        sentence = gsub("CAPS13", ' ', sentence)
        sentence = gsub("CAPS14", ' ', sentence)
        sentence = gsub("CAPS15", ' ', sentence)
        sentence = gsub("CAPS16", ' ', sentence)
        sentence = gsub("CAPS17", ' ', sentence)
        sentence = gsub("CAPS18", ' ', sentence)
        sentence = gsub("CAPS19", ' ', sentence)
        sentence = gsub("CAPS2", ' ', sentence)
        sentence = gsub("CAPS20", ' ', sentence)
        sentence = gsub("CAPS21", ' ', sentence)
        sentence = gsub("CAPS22", ' ', sentence)
        sentence = gsub("CAPS23", ' ', sentence)
        sentence = gsub("CAPS24", ' ', sentence)
        sentence = gsub("CAPS25", ' ', sentence)
        sentence = gsub("CAPS26", ' ', sentence)
        sentence = gsub("CAPS27", ' ', sentence)
        sentence = gsub("CAPS28", ' ', sentence)
        sentence = gsub("CAPS29", ' ', sentence)
        sentence = gsub("CAPS3", ' ', sentence)
        sentence = gsub("CAPS30", ' ', sentence)
        sentence = gsub("CAPS32", ' ', sentence)
        sentence = gsub("CAPS33", ' ', sentence)
        sentence = gsub("CAPS34", ' ', sentence)
        sentence = gsub("CAPS35", ' ', sentence)
        sentence = gsub("CAPS36", ' ', sentence)
        sentence = gsub("CAPS38", ' ', sentence)
        sentence = gsub("CAPS39", ' ', sentence)
        sentence = gsub("CAPS4", ' ', sentence)
        sentence = gsub("CAPS40", ' ', sentence)
        sentence = gsub("CAPS41", ' ', sentence)
        sentence = gsub("CAPS5", ' ', sentence)
        sentence = gsub("CAPS6", ' ', sentence)
        sentence = gsub("CAPS7", ' ', sentence)
        sentence = gsub("CAPS8", ' ', sentence)
        sentence = gsub("CAPS9", ' ', sentence)
        sentence = gsub("CITY1", ' ', sentence)
        sentence = gsub("DATE1", ' ', sentence)
        sentence = gsub("DATE2", ' ', sentence)
        sentence = gsub("DATE3", ' ', sentence)
        sentence = gsub("DATE4", ' ', sentence)
        sentence = gsub("DATE5", ' ', sentence)
        sentence = gsub("DATE6", ' ', sentence)
        sentence = gsub("DR1", ' ', sentence)
        sentence = gsub("DR2", ' ', sentence)
        sentence = gsub("EMAIL1", ' ', sentence)
        sentence = gsub("LOCATION1", ' ', sentence)
        sentence = gsub("LOCATION10", ' ', sentence)
        sentence = gsub("LOCATION11", ' ', sentence)
        sentence = gsub("LOCATION12", ' ', sentence)
        sentence = gsub("LOCATION2", ' ', sentence)
        sentence = gsub("LOCATION3", ' ', sentence)
        sentence = gsub("LOCATION4", ' ', sentence)
        sentence = gsub("LOCATION5", ' ', sentence)
        sentence = gsub("LOCATION6", ' ', sentence)
        sentence = gsub("LOCATION7", ' ', sentence)
        sentence = gsub("LOCATION8", ' ', sentence)
        sentence = gsub("LOCATION9", ' ', sentence)
        sentence = gsub("MONEY1", ' ', sentence)
        sentence = gsub("MONEY2", ' ', sentence)
        sentence = gsub("MONEY3", ' ', sentence)
        sentence = gsub("MONEY4", ' ', sentence)
        sentence = gsub("MONTH1", ' ', sentence)
        sentence = gsub("NUM1", ' ', sentence)
        sentence = gsub("NUM10", ' ', sentence)
        sentence = gsub("NUM11", ' ', sentence)
        sentence = gsub("NUM12", ' ', sentence)
        sentence = gsub("NUM13", ' ', sentence)
        sentence = gsub("NUM2", ' ', sentence)
        sentence = gsub("NUM3", ' ', sentence)
        sentence = gsub("NUM4", ' ', sentence)
        sentence = gsub("NUM5", ' ', sentence)
        sentence = gsub("NUM6", ' ', sentence)
        sentence = gsub("NUM7", ' ', sentence)
        sentence = gsub("NUM8", ' ', sentence)
        sentence = gsub("NUM9", ' ', sentence)
        sentence = gsub("ORGANIZATION1", ' ', sentence)
        sentence = gsub("ORGANIZATION2", ' ', sentence)
        sentence = gsub("ORGANIZATION3", ' ', sentence)
        sentence = gsub("ORGANIZATION4", ' ', sentence)
        sentence = gsub("ORGANIZATION5", ' ', sentence)
        sentence = gsub("ORGANIZATION6", ' ', sentence)
        sentence = gsub("PERCENT1", ' ', sentence)
        sentence = gsub("PERCENT2", ' ', sentence)
        sentence = gsub("PERCENT3", ' ', sentence)
        sentence = gsub("PERCENT4", ' ', sentence)
        sentence = gsub("PERCENT5", ' ', sentence)
        sentence = gsub("PERCENT6", ' ', sentence)
        sentence = gsub("PERCENT7", ' ', sentence)
        sentence = gsub("PERSON1", ' ', sentence)
        sentence = gsub("PERSON2", ' ', sentence)
        sentence = gsub("PERSON3", ' ', sentence)
        sentence = gsub("PERSON4", ' ', sentence)
        sentence = gsub("PERSON5", ' ', sentence)
        sentence = gsub("PERSON6", ' ', sentence)
        sentence = gsub("PERSON7", ' ', sentence)
        sentence = gsub("STATE1", ' ', sentence)
        sentence = gsub("TIME1", ' ', sentence)
        sentence = gsub("TIME2", ' ', sentence)
    }

#remove unwanted columns in the train data to combine all the data
data <- data[,c("essay_id","essay_set","essay")]
data$sset <- 1
valid <- valid[,c("essay_id","essay_set","essay")]
valid$sset <- 2
#test <- test[,c("essay_id","essay_set","essay")]
#test$sset <- 3

text <- rbind(data, valid) #, test)

text$essay <- word.list (text$essay)


##############################
# Create Document Term matrix
##############################
dtm <- create_matrix(cbind(text$essay)
                     ,language="english"
                     ,removeNumbers=TRUE
                     ,toLower = TRUE
                     ,removeStopwords = TRUE
                     ,ngramLength = 2
                        )

#######################################
#######################################
# LDA modelling
#######################################
#######################################

# function to convert to LDA data format 
convert <- function(x) {
  split.matrix <- 
    function (x, f, drop = FALSE, ...) 
      lapply(split(seq_len(ncol(x)), f, drop = drop, ...),
             function(ind) x[,ind, drop = FALSE])
  
  documents <- vector(mode = "list", length = nrow(x))
  documents[row_sums(x) > 0] <- split(rbind(as.integer(x$j) - 1L, as.integer(x$v)), as.integer(x$i))
  documents[row_sums(x) == 0] <- rep(list(matrix(integer(), ncol = 0, nrow = 2)), sum(row_sums(x) == 0))
  names(documents) <- rownames(x)
  list(documents = documents,
       vocab = colnames(x))
}

# convert to LDA data format
ldaformat <- convert(dtm)
documents <- ldaformat$documents
vocab <- ldaformat$vocab


K <- 8 ## Num clusters
set.seed(100) # remove randomness

result <- lda.collapsed.gibbs.sampler(documents
                                        ,K  ## Num clusters
                                        ,vocab
                                        ,200  ## Num iterations
                                        ,0.1
                                        ,0.1
                                        ,compute.log.likelihood=TRUE) 

# get LDA feature
LDA_features <- t(result$document_sums)

LDA_features <- data.frame(cbind(text$essay_id,text$sset,text$essay_set,LDA_features))
LDA_features_train <- LDA_features[LDA_features[,2]==1,c(1,4:11)]
colnames(LDA_features_train) <- c("essay_id","EJ_LDA_Topic1_2gram","EJ_LDA_Topic2_2gram","EJ_LDA_Topic3_2gram","EJ_LDA_Topic4_2gram","EJ_LDA_Topic5_2gram","EJ_LDA_Topic6_2gram","EJ_LDA_Topic7_2gram","EJ_LDA_Topic8_2gram")

LDA_features_valid <- LDA_features[LDA_features[,2]==2,c(1,4:11)]
colnames(LDA_features_valid) <- c("essay_id","EJ_LDA_Topic1_2gram","EJ_LDA_Topic2_2gram","EJ_LDA_Topic3_2gram","EJ_LDA_Topic4_2gram","EJ_LDA_Topic5_2gram","EJ_LDA_Topic6_2gram","EJ_LDA_Topic7_2gram","EJ_LDA_Topic8_2gram")

#LDA_features_test <- LDA_features[LDA_features[,2]==3,c(1,4:11)]
#colnames(LDA_features_test) <- c("essay_id","EJ_LDA_Topic1_2gram","EJ_LDA_Topic2_2gram","EJ_LDA_Topic3_2gram","EJ_LDA_Topic4_2gram","EJ_LDA_Topic5_2gram","EJ_LDA_Topic6_2gram","EJ_LDA_Topic7_2gram","EJ_LDA_Topic8_2gram")

write.csv(LDA_features_train, file = "Features/EJ_LDA_8topic_2gram.training.csv", quote = FALSE, row.names = FALSE)
write.csv(LDA_features_valid, file = "Features/EJ_LDA_8topic_2gram.valid.csv", quote = FALSE, row.names = FALSE)
#write.csv(LDA_features_test, file = "Features/EJ_LDA_8topic_2gram.test.csv", quote = FALSE, row.names = FALSE)

rm(LDA_features_train,LDA_features_valid) 
  

#############################################################################################


###################################
# Build function to create tdm
###################################

create_tdm <- 
  function (textColumns, language = "en", minDocFreq = 1, minWordLength = 3, 
            ngramLength = 0, removeNumbers = FALSE, removePunctuation = TRUE, 
            removeSparseTerms = 0, removeStopwords = TRUE, selectFreqTerms = 0, 
            stemWords = FALSE, stripWhitespace = TRUE, toLower = TRUE, 
            weighting = weightTf) 
  {
    stem_words <- function(x, language) {
      corpus <- Corpus(VectorSource(x), readerControl = list(language = language))
      matrix <- TermDocumentMatrix(corpus, control = control)
      tokens <- colnames(matrix)
      tokens <- substr(tokens, 1, 255)
      stemmed <- wordStem(tokens, language = language)
      return(iconv(paste(stemmed, collapse = " "), to = "UTF8", 
                   sub = "byte"))
    }
    select_topFreq <- function(x, language, cutoff, control) {
      corpus <- Corpus(VectorSource(x), readerControl = list(language = language))
      matrix <- as.matrix(TermDocumentMatrix(corpus, control = control))
      termCol <- cbind(colnames(matrix), matrix[1, ])
      wordDist <- sort(termCol[, 2], decreasing = TRUE)
      topWords <- rownames(as.matrix(wordDist))[0:cutoff]
      if (length(topWords) == 0) 
        return("")
      return(iconv(paste(topWords[!is.na(topWords)], collapse = " "), 
                   to = "UTF8", sub = "byte"))
    }
    tokenize_ngrams <- function(x, n = ngramLength) {
      return(rownames(as.data.frame(unclass(textcnt(x, method = "string", 
                                                    n = n)))))
    }
    if (class(textColumns) == "character") {
      trainingColumn <- textColumns
    }
    else if (class(textColumns) == "matrix") {
      trainingColumn <- c()
      for (i in 1:ncol(textColumns)) trainingColumn <- paste(trainingColumn, 
                                                             textColumns[, i])
    }
    if (ngramLength > 0) {
      control <- list(weighting = weighting, language = language, 
                      tolower = toLower, stopwords = removeStopwords, removePunctuation = removePunctuation, 
                      removeNumbers = removeNumbers, stripWhitespace = TRUE, 
                      minWordLength = minWordLength, minDocFreq = minDocFreq, 
                      tokenize = tokenize_ngrams)
    }
    else {
      control <- list(weighting = weighting, language = language, 
                      tolower = toLower, stopwords = removeStopwords, removePunctuation = removePunctuation, 
                      removeNumbers = removeNumbers, stripWhitespace = TRUE, 
                      minWordLength = minWordLength, minDocFreq = minDocFreq)
    }
    trainingColumn <- sapply(as.vector(trainingColumn, mode = "character"), 
                             iconv, to = "UTF8", sub = "byte")
    if (stemWords == TRUE) 
      trainingColumn <- sapply(as.vector(trainingColumn, mode = "character"), 
                               stem_words, language = language)
    if (selectFreqTerms > 0) 
      trainingColumn <- sapply(as.vector(trainingColumn, mode = "character"), 
                               select_topFreq, language = language, cutoff = selectFreqTerms, 
                               control = control)
    corpus <- Corpus(VectorSource(as.vector(trainingColumn, mode = "character")), 
                     readerControl = list(language = language))
    matrix <- TermDocumentMatrix(corpus, control = control)
    if (removeSparseTerms > 0) 
      matrix <- removeSparseTerms(matrix, removeSparseTerms)
    gc()
    return(matrix)
  }




#########################
# Build the dictionary
#########################

# Use the tm.lexicon.GeneralInquirer package
# install.packages("tm.lexicon.GeneralInquirer", repos = "http://datacube.wu.ac.at", type = "source")

data(H4)



######################
# Positive words
######################

positive <- scan("data/positive_words.txt", what = 'character', sep = ",") 
NewPositive <- names(H4)[unlist(lapply(H4, function(x) any(unlist(lapply(x,  function( w ) any(w %in% c("Positiv", "Pstv"))))) ))]
positive <- c (positive, NewPositive); rm(NewPositive)
# remove items that are duplicates
positive <- positive[!duplicated(positive)]


######################
# Negative words
negative <- scan("data/negative_words.txt", what = 'character', sep = ",")
NewNegative <- names(H4)[unlist(lapply(H4, function(x) any(unlist(lapply(x,  function( w ) any(w %in% c("Negativ", "Ngtv"))))) ))]
negative <- c (negative, NewNegative)  # Combine all negative words
negative <- negative[!duplicated(negative)] # remove items that are duplicates
rm(NewNegative)

######################
# Passive words
passive <- names(H4)[unlist(lapply(H4, function(x) any(unlist(lapply(x,  function( w ) any(w %in% c("Passive"))))) ))]

######################
# Active words
active <- names(H4)[unlist(lapply(H4, function(x) any(unlist(lapply(x,  function( w ) any(w %in% c("Active"))))) ))]

######################
# Active and percise words
precise <- read.csv("data/external data/Active precise words.csv", header=FALSE, quote = "")
precise <- as.character(precise[,1])


######################
# Academic word list
academic <- read.csv("data/external data/Academic Word list scores.csv", header=FALSE, quote = "")
academicSub1 <- as.character(academic[academic$V2 == 1,1])
academicSub2 <- as.character(academic[academic$V2 == 2,1])
academicSub3 <- as.character(academic[academic$V2 == 3,1])
academicSub4 <- as.character(academic[academic$V2 == 4,1])
academicSub5 <- as.character(academic[academic$V2 == 5,1])
academicSub6 <- as.character(academic[academic$V2 == 6,1])
academicSub7 <- as.character(academic[academic$V2 == 7,1])
academicSub8 <- as.character(academic[academic$V2 == 8,1])
academicSub9 <- as.character(academic[academic$V2 == 9,1])
academicSub10 <- as.character(academic[academic$V2 == 10,1])


#####################
# Transition words
transition <- read.csv("data/external data/Transition words (by ngrams).csv", header=FALSE, quote = "")
transition1 <- as.character(transition[transition$V2 == 1,1])
transition1 <- transition1[!duplicated(transition1)]
transition2 <- as.character(transition[transition$V2 == 2,1])
transition2 <- transition2[!duplicated(transition2)]
transition3 <- as.character(transition[transition$V2 == 3,1])
transition3 <- transition3[!duplicated(transition3)]
transition4 <- as.character(transition[transition$V2 == 4,1])
transition4 <- transition4[!duplicated(transition4)]
transition5 <- as.character(transition[transition$V2 == 5,1])
transition5 <- transition5[!duplicated(transition5)]


####################################
# create tdm for 1 to 5 n-grmas
# (used for transition word tagging)
####################################

tdm <- create_tdm (cbind(text$essay)     
                   ,language="english"
                   ,removeNumbers=TRUE
                   ,toLower = TRUE
                   ,removeStopwords = TRUE
                   ,stemWords=FALSE
                   ,stripWhitespace = TRUE
                   )


tdm_n2 <- create_tdm (cbind(text$essay)     
                      ,language="english"
                      ,removeNumbers=TRUE
                      ,toLower = TRUE
                      ,removeStopwords = TRUE
                      ,stemWords=FALSE
                      ,stripWhitespace = TRUE
                      ,ngramLength = 2
                      )

tdm_n3 <- create_tdm (cbind(text$essay, text$domain1_score)     
                      ,language="english"
                      ,removeNumbers=TRUE
                      ,toLower = TRUE
                      ,removeStopwords = TRUE
                      ,stemWords=FALSE
                      ,stripWhitespace = TRUE
                      ,ngramLength = 3
                      )


tdm_n4 <- create_tdm (cbind(text$essay, text$domain1_score)     
                      ,language="english"
                      ,removeNumbers=TRUE
                      ,toLower = TRUE
                      ,removeStopwords = TRUE
                      ,stemWords=FALSE
                      ,stripWhitespace = TRUE
                      ,ngramLength = 4
                      )

tdm_n5 <- create_tdm (cbind(text$essay, text$domain1_score)     
                      ,language="english"
                      ,removeNumbers=TRUE
                      ,toLower = TRUE
                      ,removeStopwords = TRUE
                      ,stemWords=FALSE
                      ,stripWhitespace = TRUE
                      ,ngramLength = 5
                      )


############################
# Sentiment scoring
############################

#sentiment
good <- tm_tag_score(tdm ,positive)
bad <- tm_tag_score(tdm, negative)
passive <- tm_tag_score(tdm, passive)
active <- tm_tag_score(tdm, active)
score1 <- data.frame(good + bad)
score2 <- data.frame(active + passive)
features <- cbind(text$essay_id, good,bad, score1, active, passive, score2, text$sset)
colnames(features) <- c("essay_id","EJ_cnt_good","EJ_cnt_bad","EJ_good_bad", "EJ_cnt_active", "EJ_cnt_passive", "EJ_Active_Passive","sset")

features_train <-  features[features$sset == 1,1:7]
features_valid <- features[features$sset == 2,1:7]
#features_test <- features[features$sset == 3,1:7]

write.csv(features_train, file = "features/EJ_features.training.csv", quote = FALSE, row.names = FALSE)
write.csv(features_valid, file = "features/EJ_features.valid.csv", quote = FALSE, row.names = FALSE)
#write.csv(features_test, file = "features/EJ_features.test.csv", quote = FALSE, row.names = FALSE)



############################
# external data scoring
############################

# Precise 
precise <- tm_tag_score(tdm ,precise) 


# Academic 
academicSub1 <- tm_tag_score(tdm ,academicSub1)
academicSub2 <- tm_tag_score(tdm ,academicSub2)
academicSub3 <- tm_tag_score(tdm ,academicSub3)
academicSub4 <- tm_tag_score(tdm ,academicSub4)
academicSub5 <- tm_tag_score(tdm ,academicSub5)
academicSub6 <- tm_tag_score(tdm ,academicSub6)
academicSub7 <- tm_tag_score(tdm ,academicSub7)
academicSub8 <- tm_tag_score(tdm ,academicSub8)
academicSub9 <- tm_tag_score(tdm ,academicSub9)
academicSub10 <- tm_tag_score(tdm ,academicSub10)
academicTotal <- cbind(academicSub1,academicSub2,academicSub3,academicSub4,academicSub5,academicSub6,academicSub7,academicSub8,academicSub9,academicSub10)
rm(academicSub1,academicSub2,academicSub3,academicSub4,academicSub5,academicSub6,academicSub7,academicSub8,academicSub9,academicSub10)

# Transition words
transition1 <- tm_tag_score(tdm ,transition1)
transition2 <- tm_tag_score(tdm_n2 ,transition2)
transition3 <- tm_tag_score(tdm_n3 ,transition3)
transition4 <- tm_tag_score(tdm_n4 ,transition4)
transition5 <- tm_tag_score(tdm_n5 ,transition5)
transitionTotal <- cbind(transition1,transition2,transition3,transition4,transition5)
rm(transition1,transition2,transition3,transition4,transition5)

extdata <- data.frame(cbind(text$essay_id, precise,academicTotal, transitionTotal,text$sset))

colnames(extdata) <- c("essay_id","EJ_Precise","EJ_cnt_Academic_sub1","EJ_cnt_Academic_sub2","EJ_cnt_Academic_sub3", "EJ_cnt_Academic_sub4", "EJ_cnt_Academic_sub5", "EJ_cnt_Academic_sub6","EJ_cnt_Academic_sub7","EJ_cnt_Academic_sub8","EJ_cnt_Academic_sub9","EJ_cnt_Academic_sub10",
                             "EJ_cnt_transition_1gram","EJ_cnt_transition_2gram","EJ_cnt_transition_3gram","EJ_cnt_transition_4gram","EJ_cnt_transition_5gram","sset"
                             )
extdata_train <-  extdata[extdata$sset == 1,1:17]
extdata_valid <- extdata[extdata$sset == 2,1:17]
#extdata_test <- extdata[extdata$sset == 3,1:17]

write.csv(extdata_train, file = "features/EJ_extdata_features.training.csv", quote = FALSE, row.names = FALSE)
write.csv(extdata_valid, file = "features/EJ_extdata_features.valid.csv", quote = FALSE, row.names = FALSE)
#write.csv(extdata_test, file = "features/EJ_extdata_features.test.csv", quote = FALSE, row.names = FALSE)



