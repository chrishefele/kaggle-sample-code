
import urllib2

LEADERBOARD_FILE  = "../data/leaderboard.txt"
LEADERBOARD_TEST1 = "../data/leaderboard-test1.txt"

fout = open(LEADERBOARD_FILE, "w")

# scrape the leaderboard from kaggle
request = urllib2.Request("https://www.kimonolabs.com/api/csv/2i3ixo7u?apikey=qtyJXfoXzVQrHxFRbRxoZ06S13CAtOjl", 
                            headers={"authorization" : "Bearer BRALL8UhSiBI78UvVPEN0PC7F0fNYtBh"})
contents = urllib2.urlopen(request).read()
fout.write(contents)

# append the old leaderboard data for version 1 of the test set 
# the leaderboard data was removed when the test set was updated to version 2
contents = open(LEADERBOARD_TEST1, "r").read()
fout.write(contents)

fout.close()

print "Wrote the leaderboard data to:", LEADERBOARD_FILE

