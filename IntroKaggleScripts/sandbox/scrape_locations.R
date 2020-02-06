
chal Wajszczuk 8 Jul 2015
## Kaggle: Introducing Kaggle Scripts
## Kaggle Users by Location

## Info:
# The idea is to make plot of Kaggle Users by their location.
# City and Country of users are taken from Kaggle Users page.
# Sections "Getting the Data" and "Preparing the Data" are commented
# due to no internet access. But you can copy it and try it yourself.




####################################################################
####################      GETTING THE DATA      ####################
####################################################################
# library(XML)
# library(RCurl)

# ## Get html code
# pageHTMLcode <- function(pageNumber=1) {
#       url <- paste("https://www.kaggle.com/users?page=", pageNumber, sep="")
#       webPage <- getURL(url, .opts=list(ssl.verifypeer=FALSE))
#       pageSource <- htmlTreeParse(webPage, useInternalNodes=TRUE)
#       return(pageSource)
# }
# 
# 
# ## Get the max pages available
# nPages <- 100
# 
# # I will proceed with only 100 pages. But code below return max number of pages available
# # nPages <- xpathSApply(pageHTMLcode(), "//div[@id='user-pages']//a", xmlValue)
# # nPages <- max(as.numeric(nPages), na.rm=TRUE)
# 
# 
# ## Get the location results
# #result <- xpathSApply(pageSource, "//p", xmlValue)
# getLocation <- function(data) {
#       result <- xpathSApply(data, "//div[@class='full-width']//p", xmlValue)
#       result <- sapply(result, function(x) gsub("^\\s+|\\s+$", "", x))
#       result <- sapply(result, function(x) gsub(" ", "", x))
#       result <- sapply(result, function(x) strsplit(x, "\r\n"))
#       result <- sapply(result, function(x) tail(x, 2))
# 
#       return(result)
# }
# 
# 
# dat <- data.frame(City=character(), Country=character())
# 
# ## Get html code for all User Pages
# for (i in 1:nPages) {
#       pageSource <- pageHTMLcode(i)
#       pageSource <- getLocation(pageSource)
#       
#       zero <- as.matrix(pageSource) == "character(0)" # in page 36 there is a guy with no information (even competitions!)
#       pageSource <- pageSource[zero=="FALSE"]
#       
#       pageSource <- as.data.frame(pageSource)
#       pageSource <- as.data.frame(t(pageSource), row.names=FALSE)
#       dat <- rbind(dat, pageSource)
# }
# 
# colnames(dat) <- c("City", "Country")
# rm(i, pageSource, zero, nPages); gc()


      #########
      # Above code crawl kaggle users page and create a data set with 
      # city and country of user. 
      # return "dat" data.frame
      ########


####################################################################
##################      PREPARING THE DATA        ##################
####################################################################
# # Remove "competition" from the data
# dat <- dat[!grepl("competit", dat$Country), ]
# # Change from factor to characters
# dat <- data.frame(sapply(dat, as.character), stringsAsFactors=FALSE)
# # Change to lower case
# dat <- data.frame(sapply(dat, tolower), stringsAsFactors=FALSE)
# 
# 
# # Cleaning Country and City names
# dat$Country[dat$Country %in% c("francemetropolitan","france,metropolitan","paris")] <- "france"
# dat[which(dat$Country == "bordeaux,france"), ] <- c("bordeaux", "france")
# 
# dat$Country[dat$Country %in% c("us","usa","unitedstatesofamerica","u.s.","u.s.a","atlanta","austin","austin,tx","berkeley",
#                                "berkeley,ca","boston","chicago","fortworth,tx","losangeles","losangles,ca","melbourne",
#                                "minneapolis","nashville","newjersey","newyork","newyorkcity","nyc","philadelphia","sanfrancisco",
#                                "sanfrancisco,ca","seattle","seattleusa","sandiego","sandiegoca","washington","washington,dc",
#                                "washingtond.c.metroarea","unitedstates")] <- "United States"
# 
# dat$Country[dat$Country %in% c("ussr","russianfederation","ussr(former)","moscow","moscow,russia","saint-petersburg")] <- "russia"
# 
# dat$Country[dat$Country %in% c("uk","edinburgh","greatbritain","london","london,uk","scotland","cambridge","england","unitedkingdom")] <- "United Kingdom"
# 
# dat$Country[dat$Country %in% c("hongkong","hongkongsar","hongkongsar,china","shanghai","china,p.r.","chinamainland","hangzhou",
#                                "beijing")] <- "china"
# 
# dat$Country[dat$Country %in% c("barcelona","espana","catalonia","esp","toledo")] <- "spain"
# 
# dat$Country[dat$Country %in% c("thenetherlands")] <- "netherlands"
# 
# 
# # Creating Country data set
# country <- data.frame(table(dat$Country))
# # Leaving only countires with Freq >= 30
# country <- subset(country, Freq>=30)
# # Making first letter upper case
# country$Var1 <- sapply(country$Var1, function(x) {
#       paste( toupper(substr(x, 1, 1)), substr(x, 2, nchar(as.character(x))), sep="" )
# })


      #########
      # In this section "dat" data.frame is preprocessed and converted into useful form.
      # Output is "country" data with names of countries and user frequencies.
      #
      # below I recreate "country" data set, due to problems with loading through script frame
      ########


country <- data.frame(
      Country=x <- c("Australia","Belgium","Brazil","Canada","China","Czechrepublic","Finland","France","Germany","Hungary","India","Iran","Israel","Italy","Japan","Netherlands","Newzealand","Poland","Russia","Singapore","Southkorea","Spain","Srilanka","Sweden","Switzerland","Taiwan","Ukraine","United Kingdom","United States"),
      Frequency=y <- c(144,42,57,187,379,31,38,230,191,33,506,32,36,66,99,93,30,77,287,81,37,124,71,36,61,105,32,275,2320)
)


####################################################################
####################      PLOT THE DATA        #####################
####################################################################

############
# Bar plot
library(ggplot2)
colnames(country) <- c("Country", "Frequency")
country_noUSA <- country[which(country$Country!="United States"),]

# With USA
country$Country <- factor(country$Country, 
                          levels=country$Country[order(country$Frequency)])

p <- ggplot(country, aes(x=Country, y=Frequency)) + 
      geom_bar(stat="identity", fill="#53cfff") +
      coord_flip() +
      ggtitle("Kaggle Users by Location (without USA)")

ggsave(p, file="Kaggle_Users_by_Location.png", width=16, height=12)


# Without USA
country_noUSA$Country <- factor(country_noUSA$Country, 
                          levels=country_noUSA$Country[order(country_noUSA$Frequency)])

g <- ggplot(country_noUSA, aes(x=Country, y=Frequency)) +
      geom_bar(stat="identity", fill="#53cfff") +
      coord_flip() +
      ggtitle("Kaggle Users by Location (without USA)")

ggsave(g, file="Kaggle_Users_by_Location(without_USA).png", width=20, height=16)



